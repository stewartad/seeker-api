from rest_framework.views import APIView
from .models import Guild, Match
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
def index(request):
    latest_match_list = Match.objects.order_by('-date')[:20]
    context = {'latest_match_list': latest_match_list}
    return render(request, 'matchreports/index.html', context)

def detail(request, match_id):
    return HttpResponse("You're looking at match %s." % match_id)

def results(request, match_id):
    response = "You're looking at the results of match %s."
    return HttpResponse(response % match_id)