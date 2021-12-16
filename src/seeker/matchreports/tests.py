from django import test
from django.test import TestCase
from django.utils.safestring import mark_safe
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import datetime, timedelta
from django.contrib.auth.models import User as DjangoUser
from django.utils import timezone
import warnings
warnings.filterwarnings(
    'error', r"DateTimeField .* received a naive datetime",
    RuntimeWarning, r'django\.db\.models\.fields',
)

from .models import *
from .api_viewsets import DeckViewSet, LeaderboardView, MatchViewSet, UserViewSet

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
        cls.guild = {
            'guild_id': 1000,
            'name': 'testguild'
        }
        cls.guild2 = {
            'guild_id': 2000,
            'name': 'testguild2'
        }
        cls.user1 = {
            'user_id': 236379624727248897,
            'name': 'yequari#2049',
        }
        cls.user2 = {
            'user_id': 770128100918296638,
            'name': 'yeq2#5677'
        }
        cls.user3 = {
            'user_id': 788139124628258816,
            'name': 'yeq3#0869'
        }
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
            Match.objects.filter(match_id=id).update(date=date)
        return response.data

    @classmethod
    def _get_matches(cls, player=None, guild_id=None, channel_id=None, start_date=None, end_date=None):
        params = {}
        if guild_id is not None:
            params['guild'] = guild_id
        if channel_id is not None:
            params['channel_id'] = channel_id
        if start_date is not None:
            params['start_date'] = int(start_date.timestamp())
        if end_date is not None:
            params['end_date'] = int(end_date.timestamp())
        if player is not None:
            params['reports__user'] = player['user_id']

        request = cls.factory.get(f'{API}/matches',
            params,
            format='json')

        force_authenticate(request, user=cls.user)
        view = MatchViewSet.as_view({'get': 'list'})
        return view(request)

    @classmethod
    def _get_leaderboard(cls, guild_id=None, channel_id=None, start_date=None, end_date=None):
        params = {}
        if guild_id is not None:
            params['guild'] = guild_id
        if channel_id is not None:
            params['channel_id'] = channel_id
        if start_date is not None:
            params['start_date'] = int(start_date.timestamp())
        if end_date is not None:
            params['end_date'] = int(end_date.timestamp())


        request = cls.factory.get(f'{API}/leaderboard',
            params, 
            format='json')
        
        force_authenticate(request, user=cls.user)
        view = LeaderboardView.as_view()
        return view(request)

    @classmethod
    def _delete_match(cls, match_id):
        request = cls.factory.delete(f'{API}/matches/{match_id}', format='json')

        force_authenticate(request, user=cls.user)
        
        view = MatchViewSet.as_view({'get': 'list', 'post': 'create', 'delete': 'destroy'})
        return view(request, pk=match_id)

# Create your tests here.
class TestAPIMethods(SeekerTestCase):

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

    def test_match_delete(self):
        first_match = self._create_match(test_guild, user_yequari, user_yeq2)
        second_match = self._create_match(test_guild, user_yequari, user_yeq2)
        irrelevant_match = self._create_match(test_guild, user_yeq2, user_yeq3)

        now = timezone.now() + timedelta(minutes=1)
        prev_hour = now - timedelta(hours=1, minutes=1)

        most_recent_matches = self._get_matches(player=user_yequari, guild_id=test_guild['guild_id'], start_date=prev_hour, end_date=now).data
        self.assertEqual(len(most_recent_matches), 2)
        self.assertEqual(second_match['match_id'], most_recent_matches[0]['match_id'])

        deletion_response = self._delete_match(most_recent_matches[0]['match_id'])
        self.assertTrue(deletion_response.status_code >= 200 and deletion_response.status_code < 300)

        most_recent_matches = self._get_matches(player=user_yequari, guild_id=test_guild['guild_id'], start_date=prev_hour, end_date=now).data
        self.assertEqual(len(most_recent_matches), 1)

class TestLeaderboard(SeekerTestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        

        # get current time
        cls.now = timezone.now()
        first = timezone.make_aware(datetime(cls.now.year, 1, 1, 0, 0, 0), timezone.utc)

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
        response = self._get_leaderboard(guild_id=self.guild2['guild_id'])

        self.assertEquals(response.status_code, 200)
        self.assertEquals(len(response.data), 2)
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), 4)
            self.assertEquals(entry.get('games_won'), 2)

    def test_leaderboard_weekly(self):
        response = self._get_leaderboard(guild_id=self.guild["guild_id"], start_date=self.weekstart, end_date=self.nextweekstart)

        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_weekly)
            self.assertEquals(entry.get('games_won'), self.expected_weekly / 2)

    def test_leaderboard_monthly(self):
        response = self._get_leaderboard(guild_id=self.guild["guild_id"], start_date=self.monthstart, end_date=self.nextmonthstart)
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_monthly)
            self.assertEquals(entry.get('games_won'), self.expected_monthly / 2)

    def test_leaderboard_yearly(self):
        response = self._get_leaderboard(guild_id=self.guild["guild_id"], start_date=self.yearstart, end_date=self.nextyearstart)
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_yearly)
            self.assertEquals(entry.get('games_won'), self.expected_yearly / 2)

    def test_leaderboard_alltime(self):
        response = self._get_leaderboard(guild_id=self.guild["guild_id"])
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_all)
            self.assertEquals(entry.get('games_won'), self.expected_all / 2)


class TestStats(SeekerTestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls._create_match(cls.guild, cls.user1, cls.user2)

    def test_stats(self):
        # TODO: improve test coverage of stats, this is a trivial test
        request = self.factory.get(f'{API}/users', format='json')
       
        force_authenticate(request, user=self.user)
        view = UserViewSet.as_view({'get': 'retrieve'})
        # import pdb; pdb.set_trace()
        response = view(request, pk=self.user1['user_id'])
        
        # assert request didn't cause error
        self.assertEquals(response.status_code, 200)
        # assert correct number of games played
        stats = response.data.get('stats')
        self.assertIsNotNone(stats['30d']['games_played'])
        self.assertIsNotNone(stats['30d']['games_won'])


class TestDeckStats(SeekerTestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.guild = {
            'guild_id': 3000,
            'name': 'testguild'
        }
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
                'guild': self.guild['guild_id'],
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
                'guild': self.guild['guild_id']
            },
            format='json')

        force_authenticate(request, user=self.user)

        view = DeckViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertEquals(response.status_code, 200)

        self.assertEquals(len(response.data), 0)


    # def test_deck_stats(self):
    #     request = self.factory.get(f'{API}/decks/', 
    #         {
    #             'guild': self.guild['guild_id'],
    #             'channel_id': test_channel,
    #         },
    #         format='json')

    #     deck = 'testdeck'
    #     force_authenticate(request, user=self.user)

    #     view = DeckViewSet.as_view({'get': 'retrieve'})
    #     response = view(request, pk=deck)

    #     self.assertEquals(response.status_code, 200)

    #     self.assertEquals(len(response.data['matches']), self.expected_matchups)