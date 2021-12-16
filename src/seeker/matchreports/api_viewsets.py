from datetime import datetime
from django.db.models import query
from django.db.models.aggregates import Sum
from django.db.models.expressions import OuterRef, Subquery
from django.utils import timezone
from rest_framework import mixins, views, viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from . import models
from .api_serializers import DeckLeaderboardSerializer, MatchSerializer, UserSerializer, get_deck_leaderboard

def setup_eager_loading(get_queryset):
    def decorator(self):
        queryset = get_queryset(self)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset
    return decorator

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    filterset_fields = ['guild', 'channel_id', 'reports__user']
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'delete']

    @setup_eager_loading
    def get_queryset(self):
        queryset = models.Match.objects.all()

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date is not None:
            date = datetime.fromtimestamp(int(start_date))
            queryset = queryset.filter(date__gte=timezone.make_aware(date, timezone.utc))
        if end_date is not None:
            date = datetime.fromtimestamp(int(end_date))
            queryset = queryset.filter(date__lt=timezone.make_aware(date, timezone.utc))
        
        return queryset.order_by('-date')


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head']
    queryset = models.User.objects.all()


class DeckViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['guild', 'channel_id']
    http_method_names = ['get', 'head']

    def list(self, request):
        guild = request.query_params.get('guild')
        channel = request.query_params.get('channel_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        serializer = DeckLeaderboardSerializer(get_deck_leaderboard(guild, channel, start_date, end_date), many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        pass


class AggregateView(views.APIView):

    def filter_reports(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        guild_id = request.query_params.get('guild')
        channel_id = request.query_params.get('channel_id')
        reports = models.Report.objects.all()

        if guild_id:
            reports = reports.filter(match__guild=guild_id)
        if start_date:
            date = timezone.make_aware(datetime.fromtimestamp(int(start_date)), timezone.utc)
            reports = reports.filter(match__date__gte=date)
        if end_date:
            date = timezone.make_aware(datetime.fromtimestamp(int(end_date)), timezone.utc)
            reports = reports.filter(match__date__lt=date)
        if channel_id:
            reports = reports.filter(match__channel_id=channel_id)

        return reports


class DeckView(AggregateView):
    pass


class LeaderboardView(AggregateView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        reports = self.filter_reports(request)

        leaderboard = []
        for user in models.User.objects.all():
            won =  user.games_won(reports) 
            played = user.games_played(reports)
            if won and played:
                winrate = won / played if played != 0 else 0
                user_entry = {
                    'user_id': user.user_id,
                    'name': user.name,
                    'games_played': played,
                    'games_won': won,
                    'winrate': winrate
                }
                leaderboard.append(user_entry)

        return Response(leaderboard)