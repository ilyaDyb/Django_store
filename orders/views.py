from django.contrib import messages
from django.conf import settings
from django.db import transaction
from django.forms import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from carts.models import Cart
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from orders.utils import send_email_payment_check

from orders.forms import CreateOrderForm
from orders.models import Order, OrderItem


@login_required
def create_order(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    if request.method == "POST":
        form = CreateOrderForm(data=request.POST)
        if form.is_valid():
            payment_on_get = form.cleaned_data["payment_on_get"]
            if int(payment_on_get) == 1:
                try:
                    with transaction.atomic():
                        user = request.user
                        cart_items = Cart.objects.filter(user=user)

                        if cart_items.exists():
                            order = Order.objects.create(
                                user=user,
                                phone_number=form.cleaned_data["phone_number"],
                                requires_delivery=form.cleaned_data[
                                    "requires_delivery"
                                ],
                                delivery_address=form.cleaned_data["delivery_address"],
                                payment_on_get=form.cleaned_data["payment_on_get"],
                            )
                            for cart_item in cart_items:
                                product = cart_item.product
                                name = cart_item.product.name
                                price = cart_item.product.sell_price()
                                quantity = cart_item.quantity

                                if product.quantity < quantity:
                                    raise ValidationError(
                                        f"Недостаточно товара {name} на складе\
                                                        В Наличии = {product.quantity}"
                                    )

                                OrderItem.objects.create(
                                    order=order,
                                    product=product,
                                    name=name,
                                    price=price,
                                    quantity=quantity,
                                )
                                product.quantity -= quantity
                                product.save()

                            cart_items.delete()

                            messages.success(request, "Заказ оформлен")
                            return redirect("user:profile")

                except ValidationError as e:
                    messages.warning(request, str(e))
                    return redirect("orders:create_order")
            elif int(payment_on_get) == 0:
                price_list = []
                quantity_list = []
                names_list = []

                try:
                    with transaction.atomic():
                        user = request.user
                        cart_items = Cart.objects.filter(user=user)

                        if cart_items.exists():
                            order = Order.objects.create(
                                user=user,
                                phone_number=form.cleaned_data["phone_number"],
                                requires_delivery=form.cleaned_data[
                                    "requires_delivery"
                                ],
                                delivery_address=form.cleaned_data["delivery_address"],
                                payment_on_get=form.cleaned_data["payment_on_get"],
                            )
                            for cart_item in cart_items:
                                product = cart_item.product
                                name = cart_item.product.name
                                price = cart_item.product.sell_price()
                                quantity = cart_item.quantity

                                price_list.append(price * quantity)
                                names_list.append(name)
                                quantity_list.append(quantity)
                                

                                if product.quantity < quantity:
                                    raise ValidationError(
                                        f"Недостаточно товара {name} на складе\
                                                        В Наличии = {product.quantity}"
                                    )

                                OrderItem.objects.create(
                                    order=order,
                                    product=product,
                                    name=name,
                                    price=price,
                                    quantity=quantity,
                                )
                            checkout_session = stripe.checkout.Session.create(
                                payment_method_types=["card"],
                                line_items=[
                                    {
                                        "price_data": {
                                            "currency": "usd",
                                            "unit_amount": int(sum(price_list) * 100),
                                            "product_data": {
                                                "name": ", ".join(
                                                    str(x) for x in names_list
                                                )
                                                + "\n Количество "
                                                + ", ".join(
                                                    str(x) for x in quantity_list
                                                ),
                                            },
                                        },
                                        "quantity": 1,
                                    },
                                ],
                                mode="payment",
                                customer_creation="always",
                                success_url=settings.DOMAIN
                                + "/orders/payment_successful?session_id={CHECKOUT_SESSION_ID}&order_id=" + f"{order.id}&price={sum(price_list)}",
                                cancel_url=settings.DOMAIN
                                + f"/orders/payment_cancelled",
                            )

                            return redirect(checkout_session.url, code=303)

                except ValidationError as e:
                    messages.warning(request, str(e))

            else:
                messages.warning(request, "Некорректное значение payment_on_get")
                return redirect("orders:create_order")
    else:
        initial = {
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
        }

        form = CreateOrderForm(initial=initial)

    context = {"title": "HOME - Оформление заказа", "form": form, "order": True}
    return render(request, "orders/create_order.html", context=context)


def payment_successful(request):
    key = request.GET.get("order_id")
    cache.add(key=key, value=request.GET.get("price"), timeout=60)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session_id = request.GET.get("session_id", None)
    session = stripe.checkout.Session.retrieve(checkout_session_id)
    customer = stripe.Customer.retrieve(session.customer)
    user_id = request.user.id
    # print(customer)
    user_payment = Order.objects.filter(
        payment_on_get=False, is_paid=False, user=user_id
    ).order_by("-id")[0]
    user_payment.stripe_checkout_id = checkout_session_id
    user_payment.is_paid = True
    user_payment.save()

    user_cart_items = Cart.objects.filter(user=request.user)

    if user_cart_items.exists():
        for cart_item in user_cart_items:
            product = cart_item.product
            quantity = cart_item.quantity

            product.quantity -= quantity
            product.save()

        user_cart_items.delete()
    price = cache.get(key=key)
    date = customer["created"]

    send_email_payment_check(email=customer["email"], price=price, date=date)

    return render(request, "orders/payment_successful.html", {"customer": customer})


def payment_cancelled(request):
    print(request)
    return render(request, "orders/payment_cancelled.html")


