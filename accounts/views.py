from django.http import HttpResponse
from .models import MyObject, Room
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
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