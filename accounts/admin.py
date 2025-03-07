from django.contrib import admin
from .models import MyObject, Room, UserRoom
# Register your models here.
admin.site.register(MyObject)
admin.site.register(Room)
admin.site.register(UserRoom)