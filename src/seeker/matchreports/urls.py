from django.urls import path, include, re_path
from rest_framework import routers
from rest_framework.schemas import get_schema_view
from . import views
from . import api_viewsets as api

router = routers.SimpleRouter()
router.register(r'matches', api.MatchViewSet, 'match')
router.register(r'leaderboard', api.LeaderboardViewSet, 'leaderboard')
router.register(r'decks', api.DeckViewSet, 'decks')

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('<int:match_id>/', views.detail, name='detail'),
]