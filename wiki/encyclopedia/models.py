from django.db import models
from django import forms

# Create your models here.

#Class for Search Form
class SearchForm(forms.Form):
    query = forms.CharField(label="Search Encyclopedia")

#Class for New Page Form
class New_PageForm(forms.Form):
    title = forms.CharField(label="Enter your title here")
    content = forms.CharField(widget=forms.Textarea(attrs=
    {"rows":5, "cols":10}), label="Enter your entry")

                              