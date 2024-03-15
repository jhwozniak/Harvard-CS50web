from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("search", views.search, name="search"),
    path("new_entry", views.new_entry, name="new_entry"),
    path("edit", views.edit, name="edit"),
    path("draw", views.draw, name="draw"),    
    path("<str:title>", views.entry, name="entry")
]
