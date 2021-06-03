from django.db.models.aggregates import Sum
from django.db.models.expressions import OuterRef, Subquery
from . import models
from django.shortcuts import render
from django.http import HttpResponse

def get_leaderboard(guild):
    # TODO: Filter by date
    reports = models.Report.objects.filter(user=OuterRef('user_id')).values('user_id').annotate(game_wins=Sum('games')).values('game_wins')[:1]
    queryset = models.User.objects.filter(report__match__guild=guild) \
        .annotate(won_games=Subquery(reports)) \
        .annotate(total_games=Sum('report__match__reports__games')) \
        .order_by('-total_games')
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