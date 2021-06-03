from django.db.models import Sum
from django.db.models.expressions import OuterRef, Subquery
from django.db.models.query_utils import Q
from rest_framework import serializers, viewsets, permissions
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.response import Response
from . import models

def setup_eager_loading(get_queryset):
    def decorator(self):
        queryset = get_queryset(self)
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset
    return decorator



# Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = '__all__'


class ReportSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = models.Report
        fields = ('user', 'games', 'deck')

class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Guild
        fields = ('name',)

class LeaderboardSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            'user_id': instance.user_id,
            'name': instance.name,
            'games_played': instance.total_games,
            'games_won': instance.won_games,
            'winrate': round(instance.won_games / instance.total_games * 100, 1)
        }

class MatchSerializer(serializers.ModelSerializer):
    reports = ReportSerializer(read_only=True, many=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.select_related('guild')
        queryset = queryset.prefetch_related('reports', 'reports__user')
        return queryset

    class Meta:
        model = models.Match
        fields = ('match_id', 'date', 'channel_id', 'guild', 'reports')
        depth = 2


# View Sets

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    filterset_fields = ['guild', 'channel_id', 'reports__user']

    @setup_eager_loading
    def get_queryset(self):
        return models.Match.objects.all()

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = models.User.objects.all()
#     serializer_class = UserSerializer

class LeaderboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    def list(self, request):
        guild = request.query_params.get('guild_id')

        reports = models.Report.objects.filter(user=OuterRef('user_id')).values('user_id').annotate(game_wins=Sum('games')).values('game_wins')[:1]
        queryset = models.User.objects.filter(report__match__guild=guild) \
            .annotate(won_games=Subquery(reports)) \
            .annotate(total_games=Sum('report__match__reports__games')) \
            .order_by('-total_games')
        serializer = LeaderboardSerializer(queryset, many=True)
        return Response(serializer.data)