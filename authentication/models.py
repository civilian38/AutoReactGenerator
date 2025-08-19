from django.contrib.auth.models import AbstractUser
from django.db import models
from encrypted_model_fields.fields import EncryptedCharField

class ARUser(AbstractUser):
    nickname = models.CharField(max_length=20, null=False, blank=True)
    bio = models.TextField(null=True, blank=True)
    gemini_key_encrypted = EncryptedCharField(max_length=250)

    def __str__(self):
        if self.nickname:
            return self.nickname
        return self.username