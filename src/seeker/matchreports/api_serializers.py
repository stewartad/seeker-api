from . import models
from rest_framework import serializers
from datetime import datetime, timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ('user_id', 'name')
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


class LeaderboardSerializer(serializers.Serializer):
    def to_representation(self, instance):
        winrate = instance.won_games / instance.total_games if instance.total_games != 0 else 0
        return {
            'user_id': instance.user_id,
            'name': instance.name,
            'games_played': instance.total_games,
            'games_won': instance.won_games,
            'winrate': winrate
        }


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
            date = int(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp()),
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