from mmap import ACCESS_DEFAULT
from socket import AddressFamily
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django import forms
from django.urls import reverse
from .models import SearchForm, New_PageForm

from . import util

def index(request):

    #If method is get
    if request.method=="GET":
        return render(request, "encyclopedia/index.html", {
            "entries": util.list_entries(), 
            "form": SearchForm()
        })
    #If method is post
    else:
        #Data user submitted and save it as form
        form = SearchForm(request.POST)

        #check if form is valid
        if form.is_valid():
            query = form.cleaned_data['query']

            entry = util.get_entry(query)

            #if desired entry is found
            if entry is not None:
                return redirect(reverse('title', kwargs={
                    'title':str(query)
                }))

            #if entry not found return search results page
            else:
                results = []
                entry_list = util.list_entries()

                for item in entry_list:
                    
                    #if query is in a section of the entry
                    if query.lower() in item.lower():
                        results.append(item)

                empty = False
                if len(results) is 0:
                    empty = True

                return render(request, "encyclopedia/search_results.html", {
                    "entry_list":results,
                    "form":SearchForm(),
                    "empty": empty
                })
        else:
            return HttpResponse("Please enter a valid form")


def title(request, title):
    
    entry = util.get_entry(title)

    #If encyclopedia entry exists
    if entry is not None:
        return render(request, "encyclopedia/title.html", {
            "title": title, 
            "entry": entry, 
            "form": SearchForm()
        })
    #If it doesn't exist
    else:
        return render(request, "encyclopedia/error.html", {
            "form": SearchForm()
        })


def new_page(request):

    #if method is get
    if request.method=="GET":
        return render(request, "encyclopedia/new_page.html",{
            "new_page_form":New_PageForm(),
            "form":SearchForm()
        })
    
    #if method is post
    else:
        form = New_PageForm(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']

            #Current list of entries
            entries = util.list_entries()

            #If entry already exists
            for entry in entries:
                if entry.lower() == title.lower():
                    return HttpResponse("<h1><b>This entry already exists!<b><h1>")

            #If it doesn't exist, add it to entry list
            util.save_entry(title, content)
            
            return redirect(reverse('title', kwargs=
                {'title': str(title)
            }))
        else:
            return HttpResponse("Please enter a valid form")

def edit_page(request, entry):
    #current entry content
    current_content = util.get_entry(entry)

    #if method is get
    if request.method=="GET":
        return render(request, "encyclopedia/edit_page.html",{
            "form": SearchForm(),
            "current_content": current_content,
            "entry": entry
        })

    #if method is post
    else:
        new_content = request.POST.get('content')
        util.save_entry(entry, new_content)
        return redirect(reverse('title', kwargs= {
            'title': str(entry)
        }))

