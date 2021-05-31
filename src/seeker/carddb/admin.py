from django.contrib import admin

from .models import BCardSubtype, BCardType, BattleCard, Card, CardSet, CharCard, CharSide, Set, StratCard, Trait
# Register your models here.

class CardSetInline(admin.StackedInline):
    model = CardSet
    extra = 0

class CardAdmin(admin.ModelAdmin):
    # fieldsets = [
    #     (None, {'fields': ['']})
    # ]
    inlines = [CardSetInline]

admin.site.register(Card, CardAdmin)
admin.site.register(Set)

admin.site.register(BattleCard)

admin.site.register(StratCard)

class CharSideInline(admin.StackedInline):
    model = CharSide
    extra = 0

class CharCardAdmin(admin.ModelAdmin):
    inlines = [CharSideInline]

admin.site.register(CharCard, CharCardAdmin)


# Essentially lookup tables with extra steps
admin.site.register(Trait)
admin.site.register(BCardType)
admin.site.register(BCardSubtype)