from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("categories", views.categories, name="categories"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("watch/<int:listing_id>", views.watch, name="watch"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("remove/<int:listing_id>", views.remove, name="remove"),
    path("bid/<int:listing_id>", views.bid, name="bid"),
    path("close/<int:listing_id>", views.close, name="close"),
    path("wins", views.wins, name="wins"),
    path("comment/<int:listing_id>", views.comment, name="comment")
]
