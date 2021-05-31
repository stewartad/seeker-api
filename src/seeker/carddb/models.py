from django.db import models
from django.db.models.fields import UUIDField
import uuid

# Card Properties
FACTIONS = [
    ('AB', 'Autobot'),
    ('DC', 'Decepticon'),
    ('MR', 'Mercenary'),
]

MODES = [
    ('ALT', 'Alt Mode'),
    ('BOT', 'Bot Mode'),
    ('BODY', 'Body Mode'),
    ('HEAD', 'Head Mode'),
    ('LEGD', 'Legend Mode'),
    ('COMB', 'Combiner Mode'),
    ('UPGR', 'Upgrade Mode')
]

PIP_COLORS = [
    ('O', 'Orange'),
    ('U', 'Blue'),
    ('B', 'Black'),
    ('W', 'White'),
    ('G', 'Green')
]

RARITIES = [
    ('C', 'Common'),
    ('U', 'Uncommon'),
    ('R', 'Rare'),
    ('SR', 'Super Rare')
]


# Create your models here.
class Card(models.Model):
    name = models.CharField(max_length=200, null=False)
    subtitle = models.CharField(max_length=200, null=True, blank=True)
    stars = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.name} - {self.subtitle}'


class Set(models.Model):
    name = models.CharField(max_length=200)
    creator = models.CharField(max_length=200) # Might abstract this to its own model
    cards = models.ManyToManyField(Card, through='CardSet')

    def __str__(self) -> str:
        return str(self.name)


class CardSet(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    set = models.ForeignKey(Set, on_delete=models.CASCADE)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    rarity = models.CharField(max_length=2, choices=RARITIES)
    cardnum = models.IntegerField()
    # cardimage field

    def __str__(self) -> str:
        return f'[{self.set.name}] {self.card.name}'


class CharCard(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE, null=False)
    faction = models.CharField(max_length=2, choices=FACTIONS, null=False)
    
    def __str__(self) -> str:
        return '{0} - {1}'.format(self.card.name, self.card.subtitle)

    class Meta:
        verbose_name = 'Character'


class Trait(models.Model):
    name = models.CharField(max_length=30)
    # add icon field

    def __str__(self) -> str:
        return str(self.name)

class CharSide(models.Model):
    character = models.ForeignKey(CharCard, on_delete=models.CASCADE)
    mode = models.CharField(max_length=4, choices=MODES)
    attack = models.IntegerField()
    defense = models.IntegerField()
    health = models.IntegerField()
    cardtext = models.TextField(max_length=4000)
    traits = models.ManyToManyField(Trait)

    def __str__(self) -> str:
        return '{0} - {1}'.format(self.character, self.mode)

    class Meta:
        verbose_name = 'Character Mode'


class Pip(models.Model):
    color = models.CharField(max_length=1, choices=PIP_COLORS)
    trait = models.ForeignKey(Trait, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return '{0} {1}'.format(self.trait, self.color)


class BCardType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Battle Card Type'


class BCardSubtype(models.Model):
    name = models.CharField(max_length=50)
    type = models.ForeignKey(BCardType, on_delete=models.CASCADE, blank=True)

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        verbose_name = 'Battle Card Subtype'


class BattleCard(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE)
    type = models.ForeignKey(BCardType, on_delete=models.CASCADE)
    subtype = models.ManyToManyField(BCardSubtype, blank=True)
    cardtext = models.TextField(max_length=4000)
    faction = models.CharField(max_length=2, choices=FACTIONS, null=True, blank=True)

    def __str__(self) -> str:
        return str(self.card.name)
    

class PipSet(models.Model):
    pip = models.ForeignKey(Pip, on_delete=models.CASCADE)
    card = models.ForeignKey(BattleCard, on_delete=models.CASCADE)
    quantity = models.IntegerField()


class StratCard(models.Model):
    card = models.OneToOneField(Card, on_delete=models.CASCADE)
    charcard = models.ForeignKey(CharCard, on_delete=models.CASCADE)
    target = models.CharField(max_length=200) # Might need more advanced model for target
    cardtext = models.TextField(max_length=4000)

    def __str__(self) -> str:
        return str(self.card.name)

    class Meta:
        verbose_name = 'Stratagem'