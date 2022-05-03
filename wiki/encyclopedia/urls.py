from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("New_Entry_Page", views.new_page, name="new_page"),
    #path("<str:entry>/edit", views.edit_page, name="edit_page"),
    path("<str:title>", views.title, name="title"),
    path("<str:entry>/edit", views.edit_page, name="edit_page")
    
]
