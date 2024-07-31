from django.db import models

# Create your models here.

#TODO: to be replaced by real database
class Tournament(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    num_players = models.IntegerField(choices=[(2, '2'), (4, '4')])

    def __str__(self):
        return self.name

#TODO: to be replaced replace by real database
class Alias(models.Model):
    alias = models.CharField(max_length=100)

    def __str__(self):
        return self.name