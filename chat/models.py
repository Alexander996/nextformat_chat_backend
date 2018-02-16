from django.contrib.auth.models import User
from django.db import models


class Chat(models.Model):
    last_date = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=30)
    users = models.ManyToManyField(User, through='ChatUser')

    class Meta:
        ordering = ['-last_date']


class ChatUser(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    join_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('chat', 'user')


class Message(models.Model):
    auto_date = models.DateTimeField(auto_now_add=True)
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    text = models.TextField()

    class Meta:
        ordering = ['-auto_date']
