from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max
from .models import User, Bid, Comment, Category, Listing, Watchlist


# displays all active listings
def index(request):      
    listings = Listing.objects.filter(is_active=True)  
    won_listings = count_won(request)
    
    return render(request, "auctions/index.html", {
        "listings" : listings,
        "won_listings" : won_listings        
    })
    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

# creates new listing
def create(request):
    if request.method == "POST":
        # accessing submitted data
        title = request.POST["title"]
        description = request.POST["description"]
        category = request.POST["category"]
        category_id = Category.objects.get(name=category)
        image = request.POST["image"]
        
        # client-side validation
        if not title or not description or not image:
            return HttpResponse("Please fill in ALL required fields.")
        
        try:
            starting_price = float(request.POST["starting_price"])
        except ValueError:
            return HttpResponse("Starting price must be a POSITIVE NUMBER!")
        if starting_price <= 0:
            return HttpResponse("Starting price must be a POSITIVE NUMBER!")
        
        # creating and saving new Listing object
        listing = Listing(title=title, description=description, category_id=category_id, is_active=True, current_price=starting_price, user_id=request.user, image=image)
        listing.save()
        return HttpResponseRedirect(reverse("index"))
        
    else:          
        return render(request, "auctions/create.html", {
            "categories" : Category.objects.all()
        })
    
# filters listings by categories
def categories(request):
    if request.method == "POST":
        selected_category = request.POST["category"]
        selected_category_id = Category.objects.get(name=selected_category)
        return render(request, "auctions/index.html", {
            "category" : selected_category,
            "filtered_listings" : Listing.objects.filter(category_id=selected_category_id, is_active=True)
        }) 
    else:
        categories = Category.objects.all()
        return render(request, "auctions/categories.html", {
            "categories" : categories
        })
    
# displays listing details
def listing(request, listing_id):
    user_is_owner = False
    listing = Listing.objects.get(pk=listing_id)
    if request.user == listing.user_id:
        user_is_owner = True
    comments = listing.comment.all()
    return render(request, "auctions/listing.html", {
        "listing" : listing,
        "user_is_owner" : user_is_owner,
        "comments" : comments 
    })

# adds listing to user's watchlist
def watch(request, listing_id):
    if request.method == "POST":
        user = request.user        
        listing = Listing.objects.get(pk=listing_id)        
    
        # handle exception  
        try:
            watchlist = Watchlist.objects.get(user_id=user)
        except Watchlist.DoesNotExist:
            watchlist = None       
        
        # if user has no watchlist, create and add listing
        if watchlist is None:        
            new_watchlist = Watchlist(user_id=user)
            new_watchlist.save()            
            listing.watchlists.add(new_watchlist)
            listing.save()
            return HttpResponseRedirect(reverse("index"))            
        
        # if user already has watchlist
        else: 
            # if listing already on watchlist
            listings = watchlist.listings.all()
            if listing in listings:
                return HttpResponse("Listing already on Your watchlist.")
                
            # else, add listing to watchlist   
            listing.watchlists.add(watchlist)
            listing.save()   
            return HttpResponseRedirect(reverse("index"))         
            
# displays watchlist
def watchlist(request):
    user = request.user 
    try:
        watchlist = Watchlist.objects.get(user_id=user)
    except Watchlist.DoesNotExist:
        watchlist = None 
    
    if watchlist is None:
        return HttpResponse("You have no listings on Your watchlist")    
    
    return render(request, "auctions/watchlist.html", {
        "listings" : watchlist.listings.exclude(is_active=False).all()
    })

# remove listing from watchlist                
def remove(request, listing_id):
    if request.method == "POST":
        user = request.user        
        listing = Listing.objects.get(pk=listing_id) 
        watchlist = Watchlist.objects.get(user_id=user)
        listing.watchlists.remove(watchlist)
        listing.save()
        return HttpResponseRedirect(reverse("watchlist")) 

# lets user place a bid on selected listing    
def bid(request, listing_id):
    if request.method == "POST":
        # bid validation    
        listing = Listing.objects.get(pk=listing_id)
        try:
            bid = float(request.POST["bid"])
        except ValueError:
            return HttpResponse("That is not a valid NUMBER!")
        if bid < 0:
            return HttpResponse("Your bid cannot be NEGATIVE NUMBER!")
        if bid <= listing.current_price:
            return HttpResponse("Your bid must be HIGHER than the current price!") 
        if request.user == listing.user_id:
            return HttpResponse("You cannot bid on Your OWN listing!")
        # create a bid       
        new_bid = Bid(amount=bid, user_id=request.user, listing_id=listing)
        new_bid.save()
        # update current_price and save
        listing.current_price = bid
        listing.save()
        return HttpResponseRedirect(reverse("index"))

# closes the listing
def close(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        if request.user != listing.user_id:
            return HttpResponse("Only owner can close this listing!")
        else:            
            listing.is_active = False
            listing.save()
            # pointing the winner

            return HttpResponseRedirect(reverse("index"))          


# displays won listings
def wins(request):
    # if user has won any auction 
    user = request.user
    closed_listings = Listing.objects.filter(is_active=False)    
    won_listings = []
    # for each closed listing
    for closed_listing in closed_listings:
        # get list of bids
        bids = closed_listing.bid.all()
        
        # find the highest bid, skip closed listings w/t bids, 
        try: 
            max_amount = bids.aggregate(Max('amount'))        
            max_bid = bids.get(amount=max_amount["amount__max"])
        except Bid.DoesNotExist:
            continue
                
        # if this bid was made by the user, add listing to won_listings list
        if max_bid.user_id == user:
            won_listings.append(closed_listing) 

    # if won_lisitngs is non-empty, display template, else display all active listings
    if len(won_listings) != 0:
        return render(request, "auctions/wins.html", {
            "listings" : won_listings
        })
    else:
        return HttpResponse("Your list of won listings is empty, sorry!")    


# adds comment to listing
def comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        new_comment = Comment(text=request.POST["comment"], user_id=request.user, listing_id=listing)
        new_comment.save()
        return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

    
# counts won listings for user
def count_won(request):
    # if user has won any auction 
    user = request.user
    closed_listings = Listing.objects.filter(is_active=False)    
    won_listings = []
    # for each closed listing
    for closed_listing in closed_listings:
        # get list of bids
        bids = closed_listing.bid.all()
        
        # find the highest bid, skip closed listings w/t bids, 
        try: 
            max_amount = bids.aggregate(Max('amount'))        
            max_bid = bids.get(amount=max_amount["amount__max"])
        except Bid.DoesNotExist:
            continue
                
        # if this bid was made by the user, add listing to won_listings list
        if max_bid.user_id == user:
            won_listings.append(closed_listing) 
    
    return len(won_listings)       
    