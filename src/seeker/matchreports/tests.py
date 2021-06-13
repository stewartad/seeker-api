from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate

from django.contrib.auth.models import User as DjangoUser

from .models import *
from .api_viewsets import MatchViewSet

# Create your tests here.
class TestApiPost(TestCase):

    def test_match_report(self):
        match_request = {
            'reports': [
                {
                    'user': {
                        'user_id': 10,
                        'name': 'test1',
                    },                    
                    'deck': 'deck1',
                    'games': 1
                },
                {
                    'user': {
                        'user_id': 20,
                        'name': 'test2',
                    },                    
                    'deck': 'deck2',
                    'games': 2
                }
            ],
            'channel_id': 200,
            'guild': {
                'guild_id': 1000,
                'name': 'testguild'
            },
        }

        factory = APIRequestFactory()
        request = factory.post('/seekerbot/api/matches/', match_request, format='json')
        
        user = DjangoUser.objects.create_user('admin', 'admin@email.com', 'password')
        force_authenticate(request, user=user)
        
        view = MatchViewSet.as_view({'get': 'list', 'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)
