# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models

class Guild(models.Model):
    guild_id = models.CharField(primary_key=True, max_length=100)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'guilds'

    def __str__(self) -> str:
        return self.name


class Match(models.Model):
    match_id = models.AutoField(primary_key=True)
    date = models.DateTimeField()
    channel_id = models.CharField(blank=True, null=True, max_length=100)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE)

    class Meta:
        db_table = 'matches'
        verbose_name_plural = 'matches'

    def __str__(self):
        reports = Report.objects.filter(match_id=self.match_id)
        return ' '.join([f'{report.user} {report.games}' for report in reports])

class User(models.Model):
    user_id = models.CharField(primary_key=True, blank=True, null=False, max_length=100)
    name = models.CharField(blank=True, null=True, max_length=100) 

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.name


class Report(models.Model):
    report_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, models.CASCADE, related_name='reports')
    match = models.ForeignKey(Match, models.CASCADE, related_name='reports')
    games = models.IntegerField()
    deck = models.CharField(blank=True, null=True, max_length=100)

    class Meta:
        db_table = 'reports'

    def __str__(self):
        return f'{self.user} {self.games}'

    


