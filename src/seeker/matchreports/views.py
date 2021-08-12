from datetime import datetime
from django.db.models.aggregates import Sum
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.query import QuerySet
from . import models
from django.shortcuts import render
from django.http import HttpResponse

# def get_leaderboard(guild=None, date=None):
#     if date is None:
#         date = 0

def get_leaderboard(guild=None, start_date=None, end_date=None):
    if start_date is None:
        start_date = 0
    if end_date is None:
        end_date = int(datetime.now().timestamp())

    reports = models.Report.objects.all()
    if guild is not None:
        reports = reports.filter(match__guild=guild, match__date__gte=start_date, match__date__lt=end_date)
        users = models.User.objects.filter(reports__match__guild=guild)
    else:
        users = models.User.objects.all()
    reports = reports.filter(user=OuterRef('user_id'))

    won_games = reports \
        .values('user_id') \
        .annotate(won_games=Sum('games')) \
        .values('won_games')
    total_games = reports \
        .values('user_id') \
        .annotate(total_games=Sum('match__reports__games')) \
        .values('total_games')
    queryset = users \
        .annotate(won_games=Subquery(won_games)) \
        .annotate(total_games=Subquery(total_games)) \
        .distinct() \
        .order_by('-total_games', '-won_games', 'name')
    return queryset

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