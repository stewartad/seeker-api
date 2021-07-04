from django.contrib import admin

from .models import Guild, Report, User, Match

# Register your models here.
admin.site.register(Report)
admin.site.register(Match)
admin.site.register(User)
admin.site.register(Guild)