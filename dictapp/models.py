from django.db import models


class Word(models.Model):
    word = models.CharField(max_length=100)
    phonetic = models.CharField(max_length=100, null=True, blank=True)
    meanings = models.JSONField()  # Store the word meanings as JSON
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.word
