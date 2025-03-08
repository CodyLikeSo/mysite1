from django.http import HttpResponse
from .models import MyObject, Room, UserRoom, Card
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
            login(request, new_user)
        else:
            return HttpResponse("WRONG SPELL")  # Теперь вызываем встроенную функцию

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
    user = request.user  # Получаем текущего пользователя


    users_in_room = UserRoom.objects.filter(room=room).select_related("user")


    # Проверяем, есть ли запись в UserRoom для данного пользователя и комнаты
    is_user_in_room = UserRoom.objects.filter(user=user, room=room).exists()

    members = UserRoom.objects.filter(room=room)
    count_members = members.__len__()


    # Выбираем шаблон в зависимости от того, находится ли пользователь в комнате
    template_name = "accounts/logined_room.html" if is_user_in_room else "accounts/room.html"

    cards = Card.objects.filter(room=room)
    prices_cards = []
    for card in cards:
        prices_cards.append((card.price, card.user.username))

    def results(prices_cards):
        result = {}

        for number, string in prices_cards:
            if string in result:
                result[string] += number
            else:
                result[string] = number

        total_sum = sum(result.values())
        num_people = len(result)

        average = total_sum / num_people

        debts = {}
        for person, amount in result.items():
            debts[person] = amount - average

        debtors = {k: -v for k, v in debts.items() if v < 0}  # Те, кто должен
        creditors = {k: v for k, v in debts.items() if v > 0}  # Те, кто должен получить

        transactions = []
        for debtor, debt in debtors.items():
            for creditor, credit in creditors.items():
                if debt > 0 and credit > 0:
                    amount_to_pay = min(-debt, credit)
                    transactions.append({
                        'user': debtor,
                        'debt': amount_to_pay,
                        'user_to_pay': creditor
                    })
                    debtors[debtor] += amount_to_pay  # Уменьшаем долг
                    creditors[creditor] -= amount_to_pay  # Уменьшаем кредит

        return transactions
    

    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')

        new_card = Card(name=name, price=price, user=request.user, room=room)
        new_card.save()

        text_header = 'CONGRATES'
        text_inner = 'YOUR CARD IS CREATED'
        context = {'text_header':text_header, 'text_inner':text_inner}
        return render(request, "accounts/succesfull.html", context)

    context = {
        "room": room,
        "is_user_in_room": is_user_in_room,
        'users_in_room': users_in_room,
        'count_members': count_members,
        'cards': cards,
        'prices_cards': prices_cards,
        'debts_info': results(prices_cards=prices_cards)
        }
    return render(request, template_name, context)

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

def get_my_rooms(request):
    if not request.user.is_authenticated:
        return redirect("login")

    rooms = Room.objects.filter(userroom__user=request.user)  # Use reverse lookup

    context = {'rooms': rooms}
    return render(request, "accounts/get_my_rooms.html", context)

def add_card_to_room(request):
    pass