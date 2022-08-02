
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    #API Routes
    path("network/create", views.create, name="create"),
    path("network/posts/<str:type>", views.posts, name="posts"),
    path("network/profile/<str:username>", views.profile, name="profile"),
    path("network/follow/<str:person_to_follow>", views.follow, name="follow"),
    path("network/unfollow/<str:person_to_unfollow>", views.unfollow, name="unfollow"),
    path("network/save/<int:post_id>", views.save, name="save"),
    path("network/like/<int:post_id>", views.like, name="like"),
    path("network/unlike/<int:post_id>", views.unlike, name="unlike"),
    
]
    