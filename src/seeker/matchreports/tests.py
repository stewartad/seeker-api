from django import test
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User as DjangoUser

from .models import *
from .api_viewsets import DeckViewSet, LeaderboardViewSet, MatchViewSet

user_yequari = {
    'user_id': 236379624727248897,
    'name': 'yequari#2049',
}

user_yeq2 = {
    'user_id': 770128100918296638,
    'name': 'yeq2#5677'
}

user_yeq3 = {
    'user_id': 788139124628258816,
    'name': 'yeq3#0869'
}

test_guild = {
    'guild_id': 1000,
    'name': 'testguild'
}

test_channel = 200
API='/seekerbot/api'

class SeekerTestCase(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.user = DjangoUser.objects.create_user(cls.__name__, 'admin@email.com', 'password')
        cls.factory = APIRequestFactory()
        return super().setUpClass()

    @classmethod
    def _create_match(cls, guild, *users, date=None, channel_id=None, deck=True):
        # creates a match report giving each user 1 win
        # usually this means 2 games per match (i.e.) 1-1

        match_request = {
            'reports': [
                {
                    'user': user,                    
                    'deck': f'deck{i}',
                    'games': 1
                } for i, user in enumerate(users)
            ],
            'channel_id': channel_id,
            'guild': guild
        }
        if not deck:
            for report in match_request['reports']:
                report['deck'] = ''

        request = cls.factory.post(f'{API}/matches/', match_request, format='json')
        
        force_authenticate(request, user=cls.user)

        view = MatchViewSet.as_view({'get': 'list', 'post': 'create'})
        response = view(request)
        if response.status_code != 201:
            raise Exception()

        id = response.data['match_id']
        if date is not None:
            Match.objects.filter(match_id=id).update(date=int(date.timestamp()))



# Create your tests here.
class TestApiPost(SeekerTestCase):

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
            'channel_id': test_channel,
            'guild': test_guild
        }

        request = self.factory.post(f'{API}/matches/', match_request, format='json')

        force_authenticate(request, user=self.user)
        
        view = MatchViewSet.as_view({'get': 'list', 'post': 'create'})
        response = view(request)

        self.assertEqual(response.status_code, 201)


class TestMatchAggregation(SeekerTestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        cls.guild = test_guild
        cls.guild2 = {
            'guild_id': 2000,
            'name': 'testguild2'
        }
        cls.user1 = user_yequari
        cls.user2 = user_yeq2
        cls.user3 = user_yeq3

        # get current time
        cls.now = datetime.now()
        first = datetime(cls.now.year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        # calculate start of each time interval
        cls.weekstart = first.replace(month=2) - timedelta(days=first.replace(month=2).weekday())
        cls.nextweekstart = cls.weekstart + timedelta(weeks=1)
        cls.monthstart = first.replace(month=10)
        cls.nextmonthstart = cls.monthstart.replace(month=cls.monthstart.month + 1)
        cls.yearstart = first
        cls.nextyearstart = cls.yearstart.replace(year=cls.yearstart.year+1)

        cls.expected_users = 3
        cls.expected_weekly = 8
        cls.expected_monthly = 4
        cls.expected_yearly = 24
        cls.expected_all = 24

        super().setUpClass()

    @classmethod
    def setUpTestData(cls) -> None:
        # week
        cls._create_match(cls.guild, cls.user1, cls.user2, date=cls.weekstart + timedelta(days=0))
        cls._create_match(cls.guild, cls.user1, cls.user3, date=cls.weekstart + timedelta(days=0))
        cls._create_match(cls.guild, cls.user3, cls.user2, date=cls.weekstart + timedelta(days=0))

        cls._create_match(cls.guild, cls.user1, cls.user2, date=cls.weekstart + timedelta(days=6))
        cls._create_match(cls.guild, cls.user1, cls.user3, date=cls.weekstart + timedelta(days=6))
        cls._create_match(cls.guild, cls.user3, cls.user2, date=cls.weekstart + timedelta(days=6))
        
        cls._create_match(cls.guild, cls.user1, cls.user2, date=cls.weekstart + timedelta(days=7))
        cls._create_match(cls.guild, cls.user1, cls.user3, date=cls.weekstart + timedelta(days=7))
        cls._create_match(cls.guild, cls.user3, cls.user2, date=cls.weekstart + timedelta(days=7))
        
        cls._create_match(cls.guild, cls.user1, cls.user2, date=cls.weekstart + timedelta(days=8))
        cls._create_match(cls.guild, cls.user1, cls.user3, date=cls.weekstart + timedelta(days=8))
        cls._create_match(cls.guild, cls.user3, cls.user2, date=cls.weekstart + timedelta(days=8))

        # month
        cls._create_match(cls.guild, cls.user1, cls.user2, date=cls.monthstart + timedelta(weeks=0))
        cls._create_match(cls.guild, cls.user1, cls.user3, date=cls.monthstart + timedelta(weeks=0))
        cls._create_match(cls.guild, cls.user3, cls.user2, date=cls.monthstart + timedelta(weeks=0))

        # year
        cls._create_match(cls.guild, cls.user1, cls.user2, date=cls.yearstart + timedelta(weeks=8))
        cls._create_match(cls.guild, cls.user1, cls.user3, date=cls.yearstart + timedelta(weeks=8))
        cls._create_match(cls.guild, cls.user3, cls.user2, date=cls.yearstart + timedelta(weeks=8))
        # > year

        # for guild filtering
        cls._create_match(cls.guild2, cls.user1, cls.user2, date=cls.weekstart + timedelta(hours=0))
        cls._create_match(cls.guild2, cls.user1, cls.user2, date=cls.weekstart + timedelta(hours=1))

    def test_guild(self):
        request = self.factory.get(f'{API}/leaderboard',
            {
                'guild': self.guild2["guild_id"]
            }, 
            format='json')
        
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(response.data), 2)
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), 4)

    def test_leaderboard_weekly(self):
        
        request = self.factory.get(f'{API}/leaderboard',
            {
                'guild': self.guild["guild_id"],
                'start_date': int(self.weekstart.timestamp()),
                'end_date': int(self.nextweekstart.timestamp())
            }, 
            format='json')
        
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_weekly)

    def test_leaderboard_monthly(self):
        request = self.factory.get(f'{API}/leaderboard',
            {
                'guild': self.guild["guild_id"],
                'start_date': int(self.monthstart.timestamp()),
                'end_date': int(self.nextmonthstart.timestamp())
            }, 
            format='json')
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_monthly)

    def test_leaderboard_yearly(self):
        request = self.factory.get(f'{API}/leaderboard',
            {
                'guild': self.guild["guild_id"],
                'start_date': int(self.yearstart.timestamp()),
                'end_date': int(self.nextyearstart.timestamp())
            }, 
            format='json')
        
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_yearly)

    def test_leaderboard_alltime(self):
        request = self.factory.get(f'{API}/leaderboard',
            {
                'guild': self.guild["guild_id"]
            }, 
            format='json')
        
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_all)

    def test_stats_weekly(self):
        request = self.factory.get(f'{API}/leaderboard/',
            {
                'guild': self.guild["guild_id"],
                'start_date': int(self.weekstart.timestamp()),
                'end_date': int(self.nextweekstart.timestamp())
            }, 
            format='json')
       
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'retrieve'})
        # import pdb; pdb.set_trace()
        response = view(request, pk=user_yequari['user_id'])
        
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of games played
        self.assertEquals(response.data.get('games_played'), self.expected_weekly)
        self.assertEquals(response.data.get('games_won'), self.expected_weekly / 2)

    # def test_stats_monthly(self):
    #     self.assertTrue(False)

    # def test_stats_yearly(self):
    #     self.assertTrue(False)

    # def test_stats_alltime(self):
    #     self.assertTrue(False)

class TestDeckStats(SeekerTestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.guild = test_guild
        cls.expected_matchups = -1
        cls.expected_decks = 2

        cls._create_match(cls.guild, user_yequari, user_yeq2, channel_id=test_channel)
        cls._create_match(cls.guild, user_yequari, user_yeq3, channel_id=test_channel)
        
        # should not be counted
        cls._create_match(cls.guild, user_yequari, user_yeq3, channel_id=0)

        return super().setUpTestData()

    def test_deck_leaderboard(self):
        request = self.factory.get(f'{API}/decks/', 
            {
                'guild': test_guild['guild_id'],
                'channel_id': test_channel,
            },
            format='json')

        deck = 'testdeck'
        force_authenticate(request, user=self.user)

        view = DeckViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(response.data), self.expected_decks)

    def test_no_channel_in_request(self):
        request = self.factory.get(f'{API}/decks/', 
            {
                'guild': test_guild['guild_id']
            },
            format='json')

        force_authenticate(request, user=self.user)

        view = DeckViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(response.data), 0)


    def test_deck_stats(self):
        request = self.factory.get(f'{API}/decks/', 
            {
                'guild': test_guild['guild_id'],
                'channel_id': test_channel,
            },
            format='json')

        deck = 'deck1'
        force_authenticate(request, user=self.user)

        view = DeckViewSet.as_view({'get': 'retrieve'})
        response = view(request, pk=deck)

        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(response.data['matches']), self.expected_matchups)