from django.db.models.aggregates import Sum
from django.db.models.expressions import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework.fields import DictField, FloatField, IntegerField
from . import models
from rest_framework import serializers
from datetime import datetime, timezone


def get_deck_leaderboard(guild_id, channel_id, start_date=None, end_date=None):
    if channel_id is None:
        return models.Report.objects.none()
    reports = models.Report.objects.filter(match__guild=guild_id, match__channel_id=channel_id) \
        .exclude(deck__isnull=True).exclude(deck__exact='')
    if start_date is not None:
        date = datetime.fromtimestamp(int(start_date))
        reports = reports.filter(match__date__gte=date)
    if end_date is not None:
        date = datetime.fromtimestamp(int(end_date))
        reports = reports.filter(match__date__lt=date)

    won_games = reports \
        .filter(deck=OuterRef('deck')) \
        .values('deck') \
        .annotate(won_games=Sum('games')) \
        .values('won_games')
    total_games = reports \
        .filter(deck=OuterRef('deck')) \
        .values('deck') \
        .annotate(total_games=Sum('match__reports__games')) \
        .values('total_games')
    queryset = reports \
        .values('deck') \
        .annotate(won_games=Subquery(won_games)) \
        .annotate(total_games=Subquery(total_games)) \
        .distinct() \
        .order_by('-total_games', '-won_games', 'deck')
    return queryset


class UserSerializer(serializers.ModelSerializer):
    stats = DictField(child=DictField(child=FloatField()), source='recent_stats', read_only=True)

    class Meta:
        model = models.User
        fields = ('user_id', 'name', 'stats')
        extra_kwargs = {
            'user_id': {
                'validators': []
            }
        }


class ReportSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = models.Report
        fields = ('user', 'games', 'deck')


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Guild
        fields = ('guild_id', 'name')
        extra_kwargs = {
            'guild_id': {
                'validators': []
            }
        }


class DeckLeaderboardSerializer(serializers.Serializer):
    '''
    [
        {
            'deck': 'name',
            'games_played': 1,
            'games_won': 0
        }
    ]
    '''
    def to_representation(self, instance):
        won_games = instance.get('won_games')
        total_games = instance.get('total_games')
        if won_games is None:
            won_games = 0
        if total_games is None:
            total_games = 0

        winrate = won_games / total_games if total_games != 0 else 0
        return {
            'deck': instance.get('deck'),
            'games_played': total_games,
            'games_won': won_games,
            'winrate': winrate
        }


class DeckStatSerializer(serializers.Serializer):
    '''
    {
        'deck': 'name',
        'matches': [
            {
                'deck': 'name',
                'games_played': 0,
                'games_won': 0
            },
            {
                'deck': 'name',
                'games_played': 1,
                'games_won': 1
            },
        ]
    }
    '''
    def to_representation(self, instance):
        # TODO
        return super().to_representation(instance)
    


class MatchSerializer(serializers.ModelSerializer):
    reports = ReportSerializer(many=True)
    guild = GuildSerializer()

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('guild')
        queryset = queryset.prefetch_related('reports', 'reports__user')
        return queryset
        
    def create(self, validated_data):
        report_list = validated_data.get('reports')
        guild_data = validated_data.get('guild')
        guild, _ = models.Guild.objects.get_or_create(
            guild_id=guild_data.get('guild_id'), 
            defaults={'name': guild_data.get('name')}
        )
        match = models.Match.objects.create(
            date = datetime.utcnow().replace(tzinfo=timezone.utc),
            channel_id = validated_data.get('channel_id'),
            guild = guild
        )
        for report in report_list:
            user_data = report.get('user')
            user, _ = models.User.objects.get_or_create(
                user_id=user_data.get('user_id'),
                defaults={'name': user_data.get('name')}
            )
            models.Report.objects.create(
                user = user,
                match = match,
                games = report.get('games'),
                deck = report.get('deck')
            )
        return match

    class Meta:
        model = models.Match
        fields = ('match_id', 'date', 'channel_id', 'guild', 'reports')
        depth = 2
        extra_kwargs = {'date': {'required': False}}
