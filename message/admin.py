from django.contrib import admin

from .models import Message, Notice

admin.site.register(Message)
admin.site.register(Notice)
