from pyexpat import model
from unicodedata import decimal
from django.contrib.auth.models import AbstractUser
from django.db import models
from django import forms

#MODELS

class User(AbstractUser):
    pass

class Listing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    bid = models.DecimalField(max_digits=64, decimal_places=2)
    photo_url = models.URLField(blank=True)
    category = models.CharField(max_length=64, blank=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='listings')

class Bid(models.Model):
    price = models.DecimalField(max_digits=64, decimal_places=2)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name="bids", default=None)
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING)

class Comment(models.Model):
    comment = models.TextField(default=None)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, default=None)
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='comments')

class Watchlist(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.DO_NOTHING, related_name="watchlists")
    user = models.ForeignKey('User', on_delete=models.CASCADE)

class DeletedListings(models.Model):
    listing = models.ForeignKey('Listing', on_delete=models.DO_NOTHING)
    highest_bid = models.DecimalField(max_digits=64, decimal_places=2)
    winner = models.ForeignKey('User', on_delete=models.DO_NOTHING)
    
#FORMS

class CreateListing(forms.Form):

    title = forms.CharField(max_length=64, widget=forms.TextInput(attrs=
    {
        'class': 'form-control'
    }))

    description = forms.CharField(widget=forms.Textarea(attrs=
    {
        "rows":5, "cols":7, "class": "form-control"
    }), label="Enter your description")

    bid = forms.DecimalField(max_digits=64, decimal_places=2)

    photo_url = forms.URLField(required=False, widget=forms.URLInput(attrs={
        'class':'form-control'
    }))

    category = forms.CharField(required=False, max_length=64, widget=forms.TextInput(attrs={
        'class':'form-control'
    }))


class CreateBid(forms.Form):
    price = forms.DecimalField(max_digits=64, decimal_places=2)


class CreateComment(forms.Form):
    comment = forms.CharField(widget=forms.Textarea(attrs=
    {
        'class':'form-control'
    }))