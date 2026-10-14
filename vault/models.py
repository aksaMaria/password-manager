from django.db import models

# Create your models here.


from django.contrib.auth.models import User


class SavedPassword(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    website = models.CharField(max_length=100)
    username = models.CharField(max_length=150)
    encrypted_password = models.TextField()
    category = models.CharField(max_length=50, default="Other")
    notes = models.TextField(blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.website