from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.db import IntegrityError
from django.urls import reverse
from django.forms import ModelForm
from django import forms
from django.contrib.auth.decorators import login_required
from bs4 import BeautifulSoup
import requests

from .models import Query, User, Article

# Create your views here.

WEBSITES = [
    ('select', 'Select'),
    ('tech', 'TechCrunch'),
    ('giz', 'Gizmodo'),
    ('wired', 'Wired')

]

class Search(ModelForm):
    website = forms.CharField(label='Website', widget=forms.Select(choices=WEBSITES))
    query = forms.CharField(label='Keywords', widget=forms.TextInput(attrs={'class': 'search form-control'}))

    website.widget.attrs.update({'class': 'form-select dropdown'})

    class Meta:
        model = Query
        fields = ['website', 'query']

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
        return render(request, "news/login.html")
    
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))

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
        return render(request, "news/register.html")


def index(request):
    form = Search()

    if request.method == 'POST':
        website = request.POST['website']
        query = request.POST['query']
        links = []

        if website == 'TechCrunch':
            url = 'https://search.techcrunch.com/search;?p={}'.format(query)
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            articles = soup.find_all('h4', 'pb-10') 

            for i in len(articles):
                article = articles[i]
                atag = article.a
                links.append(atag.get('href'))
            
            for link in links:
                html = requests.get(link)
                soup = BeautifulSoup(html.text, 'html.parser')
                headline = soup.find('h1', 'article__title').text.strip()
                body = soup.find('p', {'id':'speakable-summary'}).text.strip()
                category = soup.find('div', 'article__primary-category')
                article_entry = Article.objects.create(headline=headline, body=body, category=category, url=link, query=query)
                article_entry.save()
        
        elif website == 'Gizmodo':
            url = 'https://gizmodo.com/search?q={}'.format(query)
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            articles = soup.find_all('div', 'cw4lnv-5') 

            for i in len(articles):
                article = articles[i]
                atag = article.a
                links.append(atag.get('href'))
            
            for link in links:
                html = requests.get(link)
                soup = BeautifulSoup(html.text, 'html.parser')
                headline = soup.find('h1', 'sc-1efpnfq-0')
                body = soup.find('div', 'sc-77igqf-0 b0fvBY')
                category = soup.find('span', 'fek4t4-1')
                article_entry = Article.objects.create(headline=headline, body=body, category=category, url=link, query=query)
                article_entry.save()
        
        else:
            url = 'https://www.wired.com/search/?q={}'.format(query)
            html = requests.get(url)
            soup = BeautifulSoup(html.text, 'html.parser')
            articles = soup.find_all('div', 'SummaryItemContent')

            for i in len(articles):
                article = articles[i]
                atag = article.a
                links.append(atag.get('href'))
            
            for link in links:
                html = requests.get(link)
                soup = BeautifulSoup(html.text, 'html.parser')
                headline = soup.find('h1', 'ContentHeaderHed')
                body = soup.find('div', 'body__inner-container')
                category = soup.find('span', 'RubricName')
                article_entry = Article.objects.create(headline=headline, body=body, category=category, url=link, query=query)
                article_entry.save()
        
        

        if website == 'Select':
            return render(request, 'news/index.html', {
                'form': form,
                'select': True
            })
        
    return render(request, 'news/index.html', {
        'form': form
    })

def likes(request):
    pass

def log(request):
    pass