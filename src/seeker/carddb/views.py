from django.http.response import HttpResponse
from django.shortcuts import render

from .models import Card, CardSet

# Create your views here.
def index(request):
    cards_list = Card.objects.all()[:20]
    context = {'cards_list': cards_list}
    return render(request, 'carddb/index.html', context)

def detail(request, id):
    card = CardSet.objects.get(id=id).card
    context = {'card': card}
    return render(request, 'carddb/detail.html', context)