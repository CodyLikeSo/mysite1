from django.http import HttpResponse
from .models import MyObject, Room, UserRoom, Card
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def main(request):
    if not request.user.is_authenticated:
        return redirect('user_login')
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
            return render(request, 'accounts/user_already_exist.html')

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
            login(request, new_user)
        else:
            text_header = "Oh No!"
            text_inner = "Username or Password was wrong!"
            context = {'text_header':text_header, 'text_inner':text_inner}
            return render(request, 'accounts/succesfull.html', context)  # Теперь вызываем встроенную функцию

        return redirect('main')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('main')

@login_required
def leave_room(request, pk):
    room = get_object_or_404(Room, id=pk)
    
    # Find the UserRoom relation
    room_user = UserRoom.objects.filter(user=request.user, room=room)

    if room_user.exists():
        room_user.delete()  # Remove the user from the room

    return redirect("main") 

@login_required
def add_room(request):
    if request.method == 'POST':
        name = request.POST.get('name')

        admin = request.user if request.user.is_authenticated else None  # Проверяем, авторизован ли пользователь

        # Создаем новый объект с указанием владельца
        new_room = Room(name=name, admin=admin)
        new_room.save()

        text_header = "Nice"
        text_inner = "You've created a new room"
        context = {'text_header':text_header, 'text_inner':text_inner}

        user_room, created = UserRoom.objects.get_or_create(user=request.user, room=new_room)
        return render(request, "accounts/succesfull.html", context)  # Замените 'main' на нужный URL

    return render(request, 'accounts/add_room.html')

@login_required
def show_rooms(request):
    if request.method == 'GET':
        rooms = Room.objects.all()
        admins = Room.objects.all()
        context = {'rooms': rooms, 'admins': admins}
        return render(request, 'accounts/show_rooms.html', context)
    return HttpResponse("...")

@login_required
def delete_room(request, pk):
    room = get_object_or_404(Room, id=pk)

    if request.user != room.admin:
        text_header = 'Oh no'
        text_inner = 'You are not admin'
        context = {'text_header':text_header, 'text_inner':text_inner}
        return render(request, "accounts/succesfull.html", context)  # Redirect back to the room page

    room.delete()
    text_header = 'Already done?'
    text_inner = 'Your room was deleted'
    context = {'text_header':text_header, 'text_inner':text_inner}
    return render(request, "accounts/succesfull.html", context)

def get_room(request, pk):
    room = get_object_or_404(Room, id=pk)
    user = request.user  

    users_in_room = UserRoom.objects.filter(room=room).select_related("user")
    is_user_in_room = UserRoom.objects.filter(user=user, room=room).exists()
    members = UserRoom.objects.filter(room=room)
    count_members = members.count()

    template_name = "accounts/logined_room.html" if is_user_in_room else "accounts/room.html"

    cards = Card.objects.filter(room=room)
    prices_cards = [(card.price, card.user.username) for card in cards]
    def results(prices_cards):
        if prices_cards:
            from collections import defaultdict

            # Подсчет общей суммы затрат и затрат каждого пользователя
            total_spent = 0
            user_spent = defaultdict(float)

            for amount, user in prices_cards:
                user_spent[user] += amount
                total_spent += amount

            # Вычисляем среднюю сумму, которую должен был потратить каждый пользователь
            num_users = len(user_spent)
            fair_share = total_spent / num_users

            # Определяем, кто должен и кто переплатил
            debtors = []
            creditors = []

            for user, spent in user_spent.items():
                balance = spent - fair_share
                if balance < 0:
                    debtors.append((user, -balance))  # Этот пользователь должен
                elif balance > 0:
                    creditors.append((user, balance))  # Этот пользователь переплатил

            # Распределяем долги
            transactions = []
            i, j = 0, 0

            while i < len(debtors) and j < len(creditors):
                debtor, debt_amount = debtors[i]
                creditor, credit_amount = creditors[j]

                transfer_amount = min(debt_amount, credit_amount)

                transactions.append({
                    'user': debtor,
                    'debt': round(transfer_amount, 2),
                    'user_to_pay': creditor
                })

                # Обновляем суммы
                debtors[i] = (debtor, debt_amount - transfer_amount)
                creditors[j] = (creditor, credit_amount - transfer_amount)

                # Убираем тех, кто полностью рассчитался
                if debtors[i][1] == 0:
                    i += 1
                if creditors[j][1] == 0:
                    j += 1

            return transactions
        return []
        
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')

        if name and price:
            Card.objects.create(name=name, price=price, user=request.user, room=room)

        return redirect('get_room', pk=room.id)  # <-- Редирект после успешного создания карты

    context = {
        "room": room,
        "is_user_in_room": is_user_in_room,
        'users_in_room': users_in_room,
        'count_members': count_members,
        'cards': cards,
        'prices_cards': prices_cards,
        'debts_info': results(prices_cards)
    }
    return render(request, template_name, context)

def cards_list(request, pk):
    room = get_object_or_404(Room, id=pk)
    cards = Card.objects.filter(room=room)

    context = {
        "cards": cards,
        "room": room,  # Add room to the context
    }
    return render(request, "accounts/cards_list.html", context)


@login_required  # Ensures only logged-in users can delete
def delete_card(request, room_pk, card_pk):
    card = get_object_or_404(Card, id=card_pk)

    # Optional: Ensure only the card owner can delete it
    if request.user == card.user:
        card.delete()

    return redirect('cards_list', pk=room_pk)  # Redirects back to the card list

@login_required
def join_room(request, pk):
    room = get_object_or_404(Room, id=pk)

    # Check if the user is already in the room
    user_room, created = UserRoom.objects.get_or_create(user=request.user, room=room)

    text_header = 'You are joined room succesfully'
    text_inner = f"{request.user.username} joined {room.name}"
    context = {'text_header': text_header, 'text_inner': text_inner}

    if created:
        return render(request, "accounts/succesfull.html", context)

    return redirect("get_room", pk=pk)  # Redirect back to the room page

@login_required
def get_my_rooms(request):
    if not request.user.is_authenticated:
        return redirect("login")

    rooms = Room.objects.filter(userroom__user=request.user)  # Use reverse lookup

    context = {'rooms': rooms}
    return render(request, "accounts/get_my_rooms.html", context)

@login_required
def add_card_to_room(request):
    pass

