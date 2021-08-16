from rest_framework import viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from . import views
from . import models
from .api_serializers import MatchSerializer, LeaderboardSerializer, get_leaderboard

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
    http_method_names = ['get', 'post', 'head']

    @setup_eager_loading
    def get_queryset(self):
        return models.Match.objects.all()

class DeckViewSet(viewsets.ViewSet):
    '''
    Response data will look like
    List:
    [
        {
            'deck': 'name',
            'games_played': 1,
            'games_won': 0
        }
    ]

    Retrieve:
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
    pass

class LeaderboardViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['guild', 'channel_id']
    http_method_names = ['get', 'head']

    def retrieve(self, request, pk=None):
        queryset = models.User.objects.all()
        guild = request.query_params.get('guild')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        user = get_object_or_404(queryset, pk=pk)
        serializer = LeaderboardSerializer(get_leaderboard(guild, start_date, end_date).filter(user_id=pk).first())
        return Response(serializer.data)

    def list(self, request):
        guild = request.query_params.get('guild')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        serializer = LeaderboardSerializer(get_leaderboard(guild, start_date, end_date), many=True)
        return Response(serializer.data)