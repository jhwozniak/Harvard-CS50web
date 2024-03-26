from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    
    def __str__(self):
        return f"{self.username}"

class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")    

    def __str__(self):
        return f"Watchlist nr: {self.id} User: {self.user_id} "

class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return f"Category: {self.name}"  
    
class Listing(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=225)
    category_id = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="listing")
    is_active = models.BooleanField(default=True)
    current_price = models.FloatField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    watchlists = models.ManyToManyField(Watchlist, blank=True, related_name="listings")
    image = models.CharField(max_length=225)

    def __str__(self):
        return f"Listing nr:{self.id} {self.title}"
    
class Bid(models.Model):
    amount = models.FloatField()
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bid")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bid")

    def __str__(self):
        return f"Bid nr: {self.id} Amount: {self.amount} Listing: {self.listing_id}"

class Comment(models.Model):
    text = models.CharField(max_length=225)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comment")
    listing_id = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comment")

    def __str__(self):
        return f"Comment nr: {self.id} Text: {self.text} User: {self.user_id} Listing: {self.listing_id}"

  
