from django.urls import path

from . import views

urlpatterns = [
    path("", views.main, name="main"),
    path("add/", views.add_object, name="add_object"),
    path("join/", views.join, name="join"),
    path("login/", views.user_login, name="user_login"),
    path("user_logout/", views.user_logout, name="user_logout"),
    path("add_room/", views.add_room, name="add_room"),
    path("show_rooms/", views.show_rooms, name="show_rooms"),
    path("get_my_rooms/", views.get_my_rooms, name="get_my_rooms"),
    path("room<str:pk>/", views.get_room, name="get_room"),
    path("room<int:pk>/join/", views.join_room, name="join_room"),
    path("room<int:pk>/leave_room/", views.leave_room, name="leave_room"),
    path("room<int:pk>/delete_room/", views.delete_room, name="delete_room"),
    path("room<int:pk>/cards_list/", views.cards_list, name="cards_list"),
    path("room/<int:room_pk>/cards_list/card/<int:card_pk>/delete/", views.delete_card, name="delete_card"),
]