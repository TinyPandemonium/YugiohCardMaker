from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.contrib.auth.models import User

class Card(models.Model):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=500)
    attribute_choices = (
        ('Dark','Dark'),
        ('Earth','Earth'),
        ('Fire','Fire'),
        ('Light','Light'),
        ('Wind','Wind'),
        ('Water','Water'),
        ('Divine','Divine'),
    )
    attribute = models.CharField(max_length=6, choices=attribute_choices, default='Dark')
    star = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(12),
            MinValueValidator(1),
        ]
    )
    attack = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(0),
        ]
    )
    defense = models.IntegerField(
        default=0,
        validators=[
            MaxValueValidator(9999),
            MinValueValidator(0),
        ]
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('detail', kwargs={'card_id': self.id})

class Photo(models.Model):
    url = models.CharField(max_length=200)
    card = models.ForeignKey(Card, on_delete=models.CASCADE)

    def __str__(self):
        return f"Photo for card_id: {self.cat_id} @{self.url}"
