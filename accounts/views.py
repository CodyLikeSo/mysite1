from django.http import HttpResponse
from .models import MyObject, Room, UserRoom
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def main(request):
    return render(request, 'accounts/main.html')

@login_required
def add_object(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        tag = request.POST.get('tag')

        owner = request.user if request.user.is_authenticated else None  # Проверяем, авторизован ли пользователь

        # Создаем новый объект с указанием владельца
        new_object = MyObject(name=name, tag=tag, owner=owner)
        new_object.save()

        return redirect('main')  # Замените 'main' на нужный URL

    return render(request, 'accounts/add_object.html')

def join(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return HttpResponse("User already exists")

        new_user = User(username=username)
        new_user.set_password(password)
        new_user.save()

        return redirect('main')
    
    return render(request, 'accounts/join.html')

def user_login(request):  # Изменили имя функции
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        new_user = authenticate(request, username=username, password=password)
        if new_user is not None:
            login(request, new_user)  # Теперь вызываем встроенную функцию

        return redirect('main')
    
    return render(request, 'accounts/login.html')

def user_logout(request):
    logout(request)
    return redirect('main')

@login_required
def add_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        admin = request.user if request.user.is_authenticated else None  # Проверяем, авторизован ли пользователь

        # Создаем новый объект с указанием владельца
        new_room = Room(name=name, admin=admin)
        new_room.save()

        return redirect('main')  # Замените 'main' на нужный URL

    return render(request, 'accounts/add_room.html')

def show_rooms(request):
    if request.method == 'GET':
        rooms = Room.objects.all()
        admins = Room.objects.all()
        context = {'rooms': rooms, 'admins': admins}
        return render(request, 'accounts/show_rooms.html', context)
    return HttpResponse("...")

def get_room(request, pk):
    room = get_object_or_404(Room, id=pk)
    users_in_room = UserRoom.objects.filter(room=room).select_related("user")  # Get users in the room

    context = {"room": room, "users_in_room": users_in_room}
    return render(request, "accounts/room.html", context)

@login_required
def join_room(request, pk):
    room = get_object_or_404(Room, id=pk)

    # Check if the user is already in the room
    user_room, created = UserRoom.objects.get_or_create(user=request.user, room=room)

    if created:
        print(f"{request.user.username} joined {room.name}")

    return redirect("get_room", pk=pk)  # Redirect back to the room page

def get_my_rooms(request):
    rooms = UserRoom.objects.all()
    out = []
    for room in rooms:
        if room.user == request.user:
            out.append(room.user)
    return HttpResponse(out)