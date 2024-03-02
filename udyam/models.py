from members.models import *
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField()

    def __str__(self):
        return self.name


class Team(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE,related_name='teams')
    team_name = models.CharField(max_length=255)
    leader = models.ForeignKey(User, related_name='leading_teams', on_delete=models.CASCADE)
    member1 = models.ForeignKey(User, related_name='team_members1', on_delete=models.CASCADE, blank=True, null=True)
    member2 = models.ForeignKey(User, related_name='team_members2', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f'{self.team_name} - Team for {self.event} led by {self.leader}'
