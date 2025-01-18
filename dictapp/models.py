from django.db import models
from django.contrib.auth.models import User


class Word(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='words', null=True)
    word = models.CharField(max_length=100)
    phonetic = models.CharField(max_length=100, null=True, blank=True)
    meanings = models.JSONField()  # Store the word meanings as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        # Each word should be unique per user
        unique_together = ['user', 'word']

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.word}"
