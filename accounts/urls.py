from django.urls import path

from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path("add/", views.add_object, name="add_object"),
    path("join/", views.join, name="join"),
    path("login/", views.user_login, name="user_login"),
    path("add_room/", views.add_room, name="add_room"),
]