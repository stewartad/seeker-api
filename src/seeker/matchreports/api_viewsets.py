from rest_framework import serializers, viewsets, permissions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

import logging

from . import views
from . import models
from .api_serializers import MatchSerializer, LeaderboardSerializer

# logger = logging.getLogger(__name__)

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
        serializer = LeaderboardSerializer(views.get_leaderboard(guild, start_date, end_date).filter(user_id=pk).first())
        return Response(serializer.data)

    def list(self, request):
        guild = request.query_params.get('guild')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        serializer = LeaderboardSerializer(views.get_leaderboard(guild, start_date, end_date), many=True)
        return Response(serializer.data)