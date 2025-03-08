from django.contrib import admin
from .models import MyObject, Room, UserRoom, Card
# Register your models here.
admin.site.register(MyObject)
admin.site.register(Room)
admin.site.register(UserRoom)
admin.site.register(Card)