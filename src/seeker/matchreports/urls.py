from django.urls import path, include, re_path
from rest_framework import routers
from . import views
from . import api

router = routers.SimpleRouter()
router.register(r'matches', api.MatchViewSet, 'match')

urlpatterns = [
    path('', views.index, name='index'),
    path('api/', include(router.urls)),
    path('<int:match_id>/', views.detail, name='detail'),
]