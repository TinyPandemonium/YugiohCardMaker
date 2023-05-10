from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.urls import reverse
from django.contrib.auth.models import User

class Card(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    attribute = models.CharField(max_length=6, default ='')
    star = models.IntegerField(
        default=1,
        validators=[
            MaxValueValidator(12),
            MinValueValidator(1),
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
