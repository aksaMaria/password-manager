from django.contrib import admin

# Register your models here.

from .models import SavedPassword

admin.site.register(SavedPassword)