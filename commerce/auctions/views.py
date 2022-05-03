# Web50 Project #2
# https://cs50.harvard.edu/web/2020/projects/2/commerce/

from typing import List
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max

from .models import User, Listing, Bid, Comment, Watchlist, DeletedListings, CreateBid, CreateComment, CreateListing

def index(request):

    if request.method == "GET":

        listings = Listing.objects.all()

        #Dict {listing, max_bid}
        max_bids = {}
        
        for listing in listings:

            #All bids for current listing
            bids = Bid.objects.filter(listing=listing)

            if len(bids) == 0: 
                max_bids[listing] = "None"
            else:
                #Max bid for this listing
                max_bid = bids.aggregate(Max('price'))['price__max']

                max_bids[listing] = max_bid

        return render(request, "auctions/index.html", {
            "listings": listings,
            "max_bids": max_bids,
            "length": len(listings)
        })
    
    else:
        #Deleting listing

        listing_id = request.POST['listing_id_close']
        listing = Listing.objects.get(id=listing_id)

        #Get highest bids and winner
        bids = Bid.objects.filter(listing=listing)
        highest_bid = bids.aggregate(Max('price'))['price__max']
        winner = bids.get(price=highest_bid).user

        #Add to DeletedListings
        deleted_listing = DeletedListings.objects.create(listing=listing, highest_bid=highest_bid, winner=winner)

        return redirect(reverse('index'))


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
        password = request.POST[
            "password"]
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

#Create listing
def create(request):
    if request.method == "POST":

        #Current user
        user = request.user

        #If user is not logged in
        if not user.is_authenticated:
            return render(request, "auctions/create.html", {
                "form": CreateListing(),
                "message": "Please log in"
            })
        
        result = CreateListing(request.POST)

        if result.is_valid():
            form = result.cleaned_data

            #All components of the form
            title = form['title']
            description = form['description']
            bid = form['bid']
            photo_url = form['photo_url']
            category= form['category']

            #Current User
            user = request.user

            listing = Listing.objects.create(title=title, description=description, 
            bid=bid, photo_url=photo_url, category=category, user=user)
            
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, "auctions/create.html", {
                "message": "Please enter a valid form"
            })
    else:
        return render(request, "auctions/create.html", {
            "form": CreateListing()
        })

#All listings for user
@login_required
def watchlist(request):
    
    #GET
    if request.method == "GET":

        #All watchlist items
        items = Watchlist.objects.filter(user=request.user)

        listings = []

        for item in items:
            listing = item.listing
            listings.append(listing)

        #Dict {listing, max_bid}
        max_bids = {}
        
        for listing in listings:

            #All bids for current listing
            bids = Bid.objects.filter(listing=listing)

            if len(bids) == 0: 
                max_bids[listing] = "None"
            else:
                #Max bid for this listing
                max_bid = bids.aggregate(Max('price'))['price__max']

                max_bids[listing] = max_bid

        return render(request, "auctions/watchlist.html", {
            "max_bids": max_bids
        })

    #POST
    if request.method == "POST":

        #If add to watchlist
        if request.POST.get('listing_id_add', False):

            user = request.user
            listing_id = request.POST['listing_id_add']
            listing = Listing.objects.get(id = listing_id)

            #Create new Watchlist entry
            item = Watchlist.objects.create(listing=listing, user=user)

        #If delete from watchlist
        elif request.POST.get('listing_id_delete', False):
            user = request.user
            listing_id = request.POST['listing_id_delete']
            listing = Listing.objects.get(id = listing_id)

            #Delete from Watchlist
            Watchlist.objects.filter(user=user).get(listing=listing).delete()

        #Other side case
        else:
            return render(reverse('watchlist'))

        return redirect(reverse('watchlist'))

#List of all categories
def categories(request):
    listings = Listing.objects.all()

    categories = []
    for listing in listings:
        category = listing.category
        if category not in categories and category!='':
            categories.append(category)

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category):
    listings = Listing.objects.filter(category=category)

    return render(request, "auctions/category.html", {
        "listings": listings
    })

#Shows current listing details
def listing(request, listing_id):

    #Current user
    user = request.user

    #Current listing
    listing = Listing.objects.get(id = listing_id)

    #All the comments for this listing
    comments = Comment.objects.filter(listing = listing)

    #All the bids for this listing
    bids = Bid.objects.filter(listing = listing)

    #Maximum bid 
    max_bid = bids.aggregate(Max('price'))['price__max']
    
    #Is in watchlist or not
    in_watchlist = False
    
    try:
        if Watchlist.objects.filter(user=user).filter(listing=listing).count()>0:
            in_watchlist = True
    except:
        pass

    #GET
    if request.method == "GET":

        #IF LISTING IS CLOSED
        if DeletedListings.objects.filter(listing=listing).count()>0:
            deleted_listing = DeletedListings.objects.get(listing=listing)
            highest_bid = deleted_listing.highest_bid
            winner = deleted_listing.winner
            return render(request, "auctions/closed.html", {
                "highest_bid": highest_bid,
                "winner": winner
            })

        current_price = 0
        if isinstance(max_bid, type(None)):
            current_price = listing.bid
        else:
            current_price = max_bid
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "max_bid": current_price, 
            "bids_length": len(bids),
            "in_watchlist": in_watchlist,
            "user":user,
            "comments": comments,
            "bid_form": CreateBid(),
            "comment_form": CreateComment() 
        })

    #POST
    else:

        #If user is not logged in
        if not user.is_authenticated:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "max_bid": max_bid, 
                "bids_length": len(bids),
                "user":user,
                "message":"Please log in",
                "comments": comments,
                "bid_form": CreateBid(),
                "comment_form": CreateComment() 
            })
            
        #Results from Bid form
        bid_result = CreateBid(request.POST)

        #Results from Comment form
        comment_result = CreateComment(request.POST)

        #If user submitted Bid form
        if bid_result.is_valid():
            bids = bid_result.cleaned_data

            #All components of form
            price = bids['price']
            listing = listing
            user = user

            #If there is no bid entry
            current_price = 0
            is_none = False

            if isinstance(max_bid, type(None)):
                current_price = listing.bid
                is_none = True
            else:
                current_price = max_bid

            #If entered price is not greater than max price
            if price<=current_price:
                return render(request, "auctions/listing.html", {
                "listing": listing,
                "max_bid": max_bid, 
                "bids_length": len(bids),
                "in_watchlist": in_watchlist,
                "user":user,
                "is_none": is_none,
                "message": f"Please enter a higher bid than ${current_price}",
                "comments": comments, 
                "bid_form": CreateBid(),
                "comment_form": CreateComment()
            })

            #Create new bid entry
            new_bid = Bid.objects.create(price=price, listing=listing, user=user)

            #Redirect to current listing 
            return redirect(reverse('listing', kwargs={
                'listing_id': int(listing_id)
            }))

        #If user submitted the Comment form
        elif comment_result.is_valid():
            comments = comment_result.cleaned_data

            #All components of form
            comment = comments['comment']
            listing = listing
            user = user

            #Create new comment entry
            new_comment = Comment.objects.create(comment=comment, listing=listing, user=user)

            #Redirect to current listing
            return redirect(reverse('listing', kwargs={
                'listing_id': int(listing_id)
            }))

        #If user submitted either form but incorrectly
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "max_bid": max_bid, 
                "in_watchlist": in_watchlist,
                "bids_length": len(bids),
                "user":user,
                "message": "Please enter a valid form",
                "comments": comments, 
                "bid_form": CreateBid(),
                "comment_form": CreateComment()
            })
        


