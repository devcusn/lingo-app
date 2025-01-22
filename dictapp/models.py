from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    word = models.CharField(max_length=100)
    phonetic = models.CharField(max_length=100, null=True, blank=True)
    meanings = models.JSONField()  # Store the word meanings as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(
        User, through='WordUser', related_name='word_collection')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.word


class WordUser(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # Each word should be unique per user
        unique_together = ['word', 'user']
        verbose_name = 'Word User Relationship'
        verbose_name_plural = 'Word User Relationships'

    def __str__(self):
        return f"{self.user.username} - {self.word.word}"
