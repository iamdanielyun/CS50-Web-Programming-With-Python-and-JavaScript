import json
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import datetime

from .models import User, Post

def index(request):
    return render(request, "network/index.html")


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@csrf_exempt
@login_required
def create(request):
    #Creating new post must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST Method Required."}, 
        status=400)
    
    data = json.loads(request.body)
    user = request.user
    content = data.get("content", "")
    date = datetime.datetime.now()

    #Add entry into Post table
    post = Post.objects.create(
        creator=user, content=content, timestamp=date
    )

    return JsonResponse({"message": "Post Created successfully."}, 
    status=201)


def posts(request, type):
    #Must be via GET
    if request.method != "GET":
        return JsonResponse({"message": "GET Method Required."}, 
        status=400)

    user = request.user
    posts = None

    #if all posts
    if type == "all":
        posts = Post.objects.all()
    #if following posts
    elif type == "following" and user.is_authenticated:
        posts = Post.objects.filter(creator__in=[people.username for people in user.following.all()])
    #if specific user
    elif type in User.objects.all():
        posts = Post.objects.filter(creator=type)
    else:
        return JsonResponse({"message": "Error"}, 
        status=400)

    #Return posts in reverse chronological order
    posts = posts.order_by("-timestamp").all()

    return JsonResponse({
            "current_user": user.username,
            "posts": [post.serialize() for post in posts]
        }, safe=False)


def profile(request, username):
    #Must be via GET
    if request.method != "GET":
        return JsonResponse({"message": "GET Method Required."}, 
        status=400)
    
    #Current user
    user = User.objects.get(username=username)

    #User information
    followers = user.followers.all().count()
    following = user.following.all().count()
    posts = Post.objects.filter(creator=user).order_by("-timestamp").all()

    return JsonResponse({
            "current_user": user.username,
            "followers_count": followers,
            "following_count": following,
            "posts": [post.serialize() for post in posts]
        }, safe=False)


@login_required
def follow(request, person_to_follow):
    #Must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST Method Required."}, 
        status=400)

    user = request.user
    person_to_follow = User.objects.get(username=person_to_follow)

    #Add follower into user
    person_to_follow.followers.add(user)

    #Add user into following
    user.following.add(person_to_follow)

    return JsonResponse({"message": "User Followed."}, 
    status=201)


@login_required
def unfollow(request, person_to_unfollow):
    #Must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST Method Required."}, 
        status=400)

    user = request.user
    person_to_unfollow = User.objects.get(username=person_to_unfollow)

    #Remove follower from user
    person_to_unfollow.followers.remove(user)

    #Remove user from following
    user.following.remove(person_to_unfollow)

    return JsonResponse({"message": "User Unfollowed."}, 
    status=201)


@login_required
def save(request, post_id):
    #Must be via PUT
    if request.method != "PUT":
        return JsonResponse({"message": "PUT Method Required."}, 
        status=400)

    username = request.user
    post = Post.objects.get(id=post_id)

    #If someone else is trying to edit post
    if username != post.creator:
        return JsonResponse({"message": "You cannot edit this post."}, 
        status=400)

    data = json.loads(request.body)
    new_content = data.content

    #Update new content
    post.content = new_content
    post.save()

    return JsonResponse({"message": "Saved."}, 
    status=201)


@login_required
def like(request, post_id):
    #Must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST Method Required."}, 
        status=400)

    post = Post.objects.get(id=post_id)
    liker = request.user

    #Add liker into this post
    post.likes.add(liker)

    return JsonResponse({"message": "Post liked."}, 
    status=201)


@login_required
def unlike(request, post_id):
    #Must be via POST
    if request.method != "POST":
        return JsonResponse({"message": "POST Method Required."}, 
        status=400)

    post = Post.objects.get(id=post_id)
    unliker = request.user

    #Remove liker from this post
    post.likes.remove(unliker)

    return JsonResponse({"message": "Post Unliked."}, 
    status=201)
