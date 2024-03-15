from django import forms
from django.shortcuts import render
from . import util
import markdown2
from django.http import HttpResponseRedirect, HttpResponse
import random

# initializing global variable to store entry title between function calls  
current_title = ""

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# shows entry
def entry(request, title):   
    # if entry does not exist, display error page
    if not util.get_entry(title):
        return render(request, "encyclopedia/error.html", {
            "page_title": title
        })
    # else, update global var and show content
    else:              
        global current_title 
        current_title = title
        return render(request, "encyclopedia/entry.html", {
            "title": markdown2.markdown(util.get_entry(title)), 
            "page_title": title
        })

# returns search results
def search(request):
    if request.method == "POST":        
        query = request.POST.get("q")
        entries = util.list_entries()
        found = False
        results = []

        # if query matches entries
        for entry in entries:
            if query.lower() == entry.lower():
                found = True                
                # render entry page
                return render(request, "encyclopedia/entry.html", {
                    "title": markdown2.markdown(util.get_entry(query)), 
                    "page_title": query
                })
        # if not found
        if not found:            
            for entry in entries:
                # if query substring of entry
                if query.lower() in entry.lower():
                    results.append(entry)

            # redirect to page with results
            return render(request, "encyclopedia/search.html", {
                "entries": results
            })

# allows to create new entry
def new_entry(request):
    if request.method == "POST":        
        title = request.POST.get("title")
        content = request.POST.get("content")

        # client-side validation
        if not title or not content:
            return HttpResponse("Please fill in both title and page content.")
        else:    
            # if title already in entries
            for entry in util.list_entries():
                if title.lower() == entry.lower():
                    return HttpResponse("Sorry, we already have such title in our encyclopedia!") 
        
            # if new title, update global var, save content to file and open this entry
            global current_title 
            current_title = title
            content = content.replace('\r\n', '\n')
            util.save_entry(title, content)
            return render(request, "encyclopedia/entry.html", {
                "title": markdown2.markdown(util.get_entry(title)), 
                "page_title": title
            })

    return render(request, "encyclopedia/new_entry.html")

# allows for entry editing
def edit(request):
    if request.method == "POST":
        content = request.POST.get("content")

        # client-side validation
        if not content:
            return HttpResponse("Sorry, page content cannot be blank.")
        else:          
            # save new content under global var (current title) and open this entry
            content = content.replace('\r\n', '\n')
            util.save_entry(current_title, content)
            return render(request, "encyclopedia/entry.html", {
                "title": markdown2.markdown(util.get_entry(current_title)), 
                "page_title": current_title
            })
    
    # renders prepopulated text area in original (Markdown) format for a given title
    return render(request, "encyclopedia/edit.html", {
        "content" : util.get_entry(current_title)
    })  

# redirects to random entry
def draw(request):
    # getting random title from existing entries
    entries = util.list_entries()
    chosen_title = random.choice(entries)
    return render(request, "encyclopedia/entry.html", {
            "title": markdown2.markdown(util.get_entry(chosen_title)), 
            "page_title": chosen_title
        })
  


        

















