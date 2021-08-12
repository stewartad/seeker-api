from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate
from datetime import datetime, timedelta, timezone
from django.contrib.auth.models import User as DjangoUser

from .models import *
from .api_viewsets import LeaderboardViewSet, MatchViewSet

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

class TestMatchAggregation(TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        
        cls.guild = Guild.objects.create(**test_guild)
        cls.guild2 = Guild.objects.create(guild_id=2000, name='testguild2')
        cls.user1 = User.objects.create(**user_yequari)
        cls.user2 = User.objects.create(**user_yeq2)
        cls.user3 = User.objects.create(**user_yeq3)

        cls.factory = APIRequestFactory()
        cls.user = DjangoUser.objects.create_user('admin', 'admin@email.com', 'password')

        # get current time
        cls.now = datetime.now()
        first = datetime(cls.now.year, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        # calculate start of each time interval
        cls.weekstart = first.replace(month=2) - timedelta(days=first.weekday())
        cls.nextweekstart = cls.weekstart + timedelta(weeks=1)
        cls.monthstart = first.replace(month=10)
        cls.nextmonthstart = cls.monthstart.replace(month=cls.monthstart.month + 1)
        cls.yearstart = first
        cls.nextyearstart = cls.yearstart.replace(year=cls.yearstart.year+1)

        cls.expected_users = 3
        cls.expected_weekly = 4
        cls.expected_monthly = 4
        cls.expected_yearly = 20
        cls.expected_all = 20

        super().setUpClass()

    @classmethod
    def setUpTestData(cls) -> None:
        # week
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=0), cls.user1, cls.user2)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=0), cls.user1, cls.user3)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=0), cls.user3, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=1), cls.user1, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=1), cls.user1, cls.user3)
        # cls._create_match(cls.weekstart + timedelta(days=1), cls.user3, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=2), cls.user1, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=2), cls.user1, cls.user3)
        # cls._create_match(cls.weekstart + timedelta(days=2), cls.user3, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=3), cls.user1, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=3), cls.user1, cls.user3)
        # cls._create_match(cls.weekstart + timedelta(days=3), cls.user3, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=4), cls.user1, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=4), cls.user1, cls.user3)
        # cls._create_match(cls.weekstart + timedelta(days=4), cls.user3, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=5), cls.user1, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=5), cls.user1, cls.user3)
        # cls._create_match(cls.weekstart + timedelta(days=5), cls.user3, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=6), cls.user1, cls.user2)
        # cls._create_match(cls.weekstart + timedelta(days=6), cls.user1, cls.user3)
        # cls._create_match(cls.weekstart + timedelta(days=6), cls.user3, cls.user2)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=7), cls.user1, cls.user2)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=7), cls.user1, cls.user3)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=7), cls.user3, cls.user2)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=8), cls.user1, cls.user2)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=8), cls.user1, cls.user3)
        cls._create_match(cls.guild, cls.weekstart + timedelta(days=8), cls.user3, cls.user2)

        # month
        cls._create_match(cls.guild, cls.monthstart + timedelta(weeks=0), cls.user1, cls.user2)
        cls._create_match(cls.guild, cls.monthstart + timedelta(weeks=0), cls.user1, cls.user3)
        cls._create_match(cls.guild, cls.monthstart + timedelta(weeks=0), cls.user3, cls.user2)

        # year
        cls._create_match(cls.guild, cls.yearstart + timedelta(weeks=8), cls.user1, cls.user2)
        cls._create_match(cls.guild, cls.yearstart + timedelta(weeks=8), cls.user1, cls.user3)
        cls._create_match(cls.guild, cls.yearstart + timedelta(weeks=8), cls.user3, cls.user2)
        # > year

    @classmethod
    def _create_match(cls, guild, date, *users):
        # creates a match report with as many games as users
        # usually this means 2 games per match (i.e.) 1-1
        match = Match.objects.create(guild=guild, date=int(date.timestamp()))
        for user in users:
            Report.objects.create(user=user, match=match, games=1)

    def test_guild(self):
        # for guild filtering
        self._create_match(self.guild2, self.weekstart + timedelta(hours=0), self.user1, self.user2)
        self._create_match(self.guild2, self.weekstart + timedelta(hours=1), self.user1, self.user2)

        request = self.factory.get(f'/seekerbot/api/leaderboard?guild={self.guild2.guild_id}', format='json')
        
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)

        self.assertTrue(response.status_code >= 200 and response.status_code < 400)

        self.assertEquals(len(response.data), 2)
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), 4)

    def test_leaderboard_weekly(self):
        
        request = self.factory.get(f'/seekerbot/api/leaderboard?guild={self.guild.guild_id}'\
            f'&start_date={ int(self.weekstart.timestamp()) }' \
            f'&end_date={ int(self.nextweekstart.timestamp()) }', format='json')
        
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertTrue(response.status_code >= 200 and response.status_code < 400)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_weekly)

    def test_leaderboard_monthly(self):
        request = self.factory.get(f'/seekerbot/api/leaderboard?guild={self.guild.guild_id}'\
            f'&start_date={ int(self.monthstart.timestamp()) }' \
            f'&end_date={ int(self.nextmonthstart.timestamp()) }', format='json')
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertTrue(response.status_code >= 200 and response.status_code < 400)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_monthly)

    def test_leaderboard_yearly(self):
        request = self.factory.get(f'/seekerbot/api/leaderboard?guild={self.guild.guild_id}'\
            f'&start_date={ int(self.yearstart.timestamp()) }' \
            f'&end_date={ int(self.nextyearstart.timestamp()) }', format='json')
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertTrue(response.status_code >= 200 and response.status_code < 400)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_yearly)

    def test_leaderboard_alltime(self):
        request = self.factory.get(f'/seekerbot/api/leaderboard?guild={self.guild.guild_id}', format='json')
        force_authenticate(request, user=self.user)
        view = LeaderboardViewSet.as_view({'get': 'list'})
        response = view(request)
        # assert request didn't cause error
        self.assertTrue(response.status_code >= 200 and response.status_code < 400)
        # assert correct number of users
        self.assertEquals(len(response.data), self.expected_users)
        # assert correct number of games played
        for entry in response.data:
            self.assertEquals(entry.get('games_played'), self.expected_all)

    # def test_stats_weekly(self):
    #     self.assertTrue(False)

    # def test_stats_monthly(self):
    #     self.assertTrue(False)

    # def test_stats_yearly(self):
    #     self.assertTrue(False)

    # def test_stats_alltime(self):
    #     self.assertTrue(False)
