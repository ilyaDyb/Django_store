from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.contrib import auth, messages
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.conf import settings
from django.core.cache import cache

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
            )
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
    user = request.user
    context = {"title": "Home - Регистрация", "form": form, "orders": orders, "user": user}
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


def reset_password_write_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
        except Exception as ex:
            messages.warning(request, "Пользователя с такой почтой не существует")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        link_for_confirm = settings.DOMAIN + reverse("users:reset_password_end", kwargs={"uidb64":uid, "token":token})
        send_email_for_confirmation(email=email, link_for_confirm=link_for_confirm)
        return redirect(reverse("user:confirm_email"))
    return render(request, "users/reset_password/write_email.html")


def reset_password_end(request, uidb64, token):
    if request.method == "POST":    
        print("request_post: TRUE")
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=str(uid.decode('utf-8')))

        except (TypeError, ValueError, User.DoesNotExist, OverflowError) as e:
            user = None
            print(e)

        if user is not None and default_token_generator.check_token(user, token):
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")

            if password1 == password2:
                user.set_password(password1)
                user.save()
                return redirect(reverse("user:login"))
            
            else:
                messages.warning(request, "Пароли не совпадают. Пожалуйста,введите пароли заново")
                return redirect(reverse("users:reset_password_end"))
            
    return render(request, "users/reset_password/reset_password.html", {"uidb64": uidb64, "token": token})


def confirm_email(request):
    return render(request, "users/reset_password/confirm_email.html")


def write_phone_number(request):
    return render(request, "users/two_step_auth/write_phone_number.html")


def confirm_phone_number(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        if len(phone_number) < 11 or len(phone_number) > 11:
            messages.warning(request, "Неверный номер телефона")
            return redirect(reverse("users:write_phone_number"))
        else:
            code = generate_unique_code()
            cache.add(key=f"code_for_{request.user.id}", value=code, timeout=60)
            cache.add(key=f"phone_number_{request.user.id}", value=phone_number, timeout=60)
            return render(request, "users/two_step_auth/confirm_phone_number.html", context={"code": code})
    else:
        return HttpResponse(status=404)
    

def final_step_phone_number(request):
    if request.method == "POST":
        key_for_code = f"code_for_{request.user.id}"
        key_for_phone = f"phone_number_{request.user.id}"
        code_from_user = request.POST.get("ver_code")
        code = cache.get(key=key_for_code)
        phone_number = cache.get(key=key_for_phone)

        if code_from_user == code:
            cache.delete(key=key_for_code)
            user = request.user
            user.phone_number = phone_number
            user.two_step_auth = True
            user.save()
            cache.delete(key=key_for_phone)
            messages.success(request, "Вы успешно подкулючили A2P")
            return redirect(reverse("users:profile"))
        
        else:
            messages.warning(request, "Неправильный код")
            return redirect(reverse("users:write_phone_number"))

    else:
        return HttpResponse(status=404)