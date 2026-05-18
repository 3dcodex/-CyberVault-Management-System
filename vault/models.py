from django.db import models
from django.contrib.auth.models import User
from .encryption import encrypt_value, decrypt_value


class Credential(models.Model):
    owner      = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credentials')
    site_name  = models.CharField(max_length=255)
    username   = models.CharField(max_length=255)
    # Stored encrypted via encrypt_value(); use .decrypted_password to read.
    password   = models.CharField(max_length=512)
    notes      = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        self.password = encrypt_value(self.password)
        super().save(*args, **kwargs)

    @property
    def decrypted_password(self) -> str:
        return decrypt_value(self.password)

    def __str__(self):
        return f"{self.site_name} ({self.username})"
