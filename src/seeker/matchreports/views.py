from django.db.models.aggregates import Sum
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.query import QuerySet
from rest_framework.generics import get_object_or_404
from . import models
from django.shortcuts import render
from django.http import HttpResponse




# Create your views here.
def index(request):
    latest_match_list = models.Match.objects.order_by('-date')[:20]
    context = {'latest_match_list': latest_match_list}
    return render(request, 'matchreports/index.html', context)

def detail(request, match_id):
    return HttpResponse("You're looking at match %s." % match_id)

def results(request, match_id):
    response = "You're looking at the results of match %s."
    return HttpResponse(response % match_id)