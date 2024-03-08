import email
from django.contrib.auth.decorators import login_required
from django.contrib import auth, messages, sessions
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from carts.models import Cart
from orders.models import Order, OrderItem

from users.forms import ProfileForm, UserLoginForm, UserRegistrationForm
from users.models import TemporaryUser, User

from users.utils import generate_unique_code, send_email_for_confirmation


def login(request):
    if request.method == "POST":
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = auth.authenticate(username=username, password=password)

            session_key = request.session.session_key

            if user:
                auth.login(request, user)
                messages.success(request, f"{username}, Вы вошли в аккаунт")

                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)

                redirect_page = request.POST.get("next", None)

                if redirect_page and redirect_page != reverse("user:logout"):
                    return HttpResponseRedirect(request.GET.get("next"))

                return HttpResponseRedirect(reverse("main:index"))
    else:
        form = UserLoginForm()

    context = {"title": "Home - Авторизация", "form": form}
    return render(request, "users/login.html", context)


def registration(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password1"]

            # Создание временного пользователя
            unique_code = generate_unique_code()
            temporary_user = TemporaryUser(
                username=username,
                email=email,
                password=password,
                unique_code=unique_code,
            )
            temporary_user.save()

            # Отправка уникального кода подтверждения почты
            send_email_for_confirmation(email, unique_code)

            # Перенаправление на контроллер с уникальным кодом
            return redirect("user:verify_email", user_id=temporary_user.id)

    else:
        form = UserRegistrationForm()

    context = {"title": "Home - Регистрация", "form": form}
    return render(request, "users/registration.html", context)


def verify_email(request, user_id):
    temporary_user = get_object_or_404(TemporaryUser, id=user_id)
    # Проверка уникального кода
    if request.method == "POST":
        session_key = request.session.session_key
        entered_code = request.POST.get("verification_code")
        if entered_code == temporary_user.unique_code:
            # Уникальный код верен, регистрируем пользователя
            user = (
                temporary_user.convert_to_user()
            )  # Замените этот метод на ваш способ создания пользователя
            user.save()
            auth.login(request, user)
            temporary_user.delete()
            if session_key:
                Cart.objects.filter(session_key=session_key).update(user=user)

            messages.success(
                request, f"{user.username}, Вы успешно зарегистрированы в аккаунт"
            )

            return HttpResponseRedirect(reverse("main:index"))
        
    email = temporary_user.email
    context = {
        "title": "Home - Подтверждение почты",
        "user_id": user_id,
        "email": email
        }
    return render(request, "users/verify_gmail.html", context)


@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileForm(
            data=request.POST, instance=request.user, files=request.FILES
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Профиль успешно обновлен")
            return HttpResponseRedirect(reverse("user:profile"))

    else:
        form = ProfileForm(instance=request.user)

    orders = (
        Order.objects.filter(user=request.user)
        .prefetch_related(
            Prefetch(
                "orderitem_set", queryset=OrderItem.objects.select_related("product")
            )
        )
        .order_by("-id")
    )
    context = {"title": "Home - Регистрация", "form": form, "orders": orders}
    return render(request, "users/profile.html", context)


def users_cart(request):
    context = {
        "check_current_page": False,
    }
    return render(request, "users/users_cart.html", context=context)


@login_required
def logout(request):
    messages.success(request, f"{request.user.username}, Вы успешно вышли")
    auth.logout(request)
    return redirect(reverse("main:index"))
