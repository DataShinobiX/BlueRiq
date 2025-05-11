from django.db import models

from django.contrib.auth.models import User


class SentenceFeedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    sentence = models.TextField()
    category = models.CharField(max_length=50)  # rule, definition, exception, external_source
    action = models.CharField(max_length=10)  # 'kept' or 'removed'
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.category} | {self.action}"
