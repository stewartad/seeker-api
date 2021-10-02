from django.db.models import query
from django.db.models.aggregates import Sum
from django.db.models.expressions import OuterRef, Subquery
from rest_framework import serializers, viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import action
from . import views
from . import models
from .api_serializers import DeckLeaderboardSerializer, MatchSerializer, LeaderboardSerializer, UserSerializer, get_deck_leaderboard

def setup_eager_loading(get_queryset):
    def decorator(self):
        queryset = get_queryset(self)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset
    return decorator

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    filterset_fields = ['guild', 'channel_id']
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'post', 'head', 'delete']

    @setup_eager_loading
    def get_queryset(self):
        queryset = models.Match.objects.all()

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        player = self.request.query_params.get('player')

        if start_date is not None:
            queryset = queryset.filter(date__gte=start_date)
        if end_date is not None:
            queryset = queryset.filter(date__lt=end_date)
        if player is not None:
            queryset = queryset.filter(reports__user=player)
        
        return queryset


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


class LeaderboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', 'head']

    def get_queryset(self):
        queryset = models.Match.objects.all()

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        guild = self.request.query_params.get('guild_id')
        channel = self.request.query_params.get('channel_id')

        if start_date is not None:
            queryset = queryset.filter(date__gte=start_date)
        if end_date is not None:
            queryset = queryset.filter(date__lt=end_date)
        if guild is not None:
            queryset = queryset.filter(guild=guild)
        if channel is not None:
            queryset = queryset.filter(channel_id=channel)
        
        return queryset

    def _get_user_stats(self):
        matches = self.get_queryset()
        reports = models.Report.objects.filter(match__in=matches)
        users = models.User.objects.filter(reports__match__in=matches)

        reports = reports.filter(user=OuterRef('user_id'))
        won_games = reports \
            .values('user_id') \
            .annotate(won_games=Sum('games')) \
            .values('won_games')
        total_games = reports \
            .values('user_id') \
            .annotate(total_games=Sum('match__reports__games')) \
            .values('total_games')
        return users \
            .annotate(won_games=Subquery(won_games)) \
            .annotate(total_games=Subquery(total_games)) \
            .distinct() \
            .order_by('-total_games', '-won_games', 'name')

    def retrieve(self, request, pk=None):
        serializer = LeaderboardSerializer(self._get_user_stats().filter(user_id=pk).first())
        return Response(serializer.data)

    def list(self, request):
        serializer = LeaderboardSerializer(self._get_user_stats(), many=True)
        return Response(serializer.data)