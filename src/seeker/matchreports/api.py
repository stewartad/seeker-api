from django.db.models import query
from rest_framework import routers, serializers, viewsets, generics
from . import models

# Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = ['name']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Report
        fields = '__all__'


class GuildSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Guild
        fields = ['name']


class MatchSerializer(serializers.ModelSerializer):
    reports = ReportSerializer(read_only=True, many=True)

    @staticmethod
    def setup_eager_loading(queryset):
        queryset = queryset.prefetch_related('reports', 'guild')
        return queryset

    class Meta:
        model = models.Match
        fields = ['date', 'reports', 'channel_id', 'guild']
        depth = 1


# View Sets

class MatchViewSet(viewsets.ModelViewSet):
    serializer_class = MatchSerializer
    filterset_fields = ['guild', 'channel_id']

    def get_queryset(self):
        queryset = models.Match.objects.all()
        queryset = self.get_serializer_class().setup_eager_loading(queryset)
        return queryset

# class GuildViewSet(viewsets.ModelViewSet):
#     queryset = models.Guild.objects.all()
#     serializer_class = GuildSerializer


# class ReportViewSet(viewsets.ModelViewSet):
#     queryset = models.Report.objects.all()
#     serializer_class = ReportSerializer

# class UserViewSet(viewsets.ModelViewSet):
#     queryset = models.User.objects.all()
#     serializer_class = UserSerializer


# List Views

class MatchList(generics.ListAPIView):
    serializer_class= MatchSerializer
    

    def get_queryset(self):
        queryset = models.Match.objects.all().prefetch_related('reports')
        guild = self.request.query_params.get('guild')
        if guild is not None:
            queryset = queryset.filter(guild=guild)
        return queryset