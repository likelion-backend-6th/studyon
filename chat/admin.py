from django.contrib import admin

from chat.models import Chat, Room


admin.site.register(Room)
admin.site.register(Chat)
