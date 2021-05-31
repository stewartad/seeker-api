from django.contrib import admin

from .models import Report, User, Match

# Register your models here.
admin.site.register(Report)
admin.site.register(Match)
admin.site.register(User)