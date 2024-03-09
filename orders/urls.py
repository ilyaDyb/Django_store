from django.urls import path

from orders import views

app_name = 'orders'

urlpatterns = [
    path("create-order/", views.create_order, name="create_order"),
    path("payment_successful/", views.payment_successful, name="payment_successful"),
    path("payment_cancelled/", views.payment_cancelled, name="payment_cancelled"),
    path("payment_stripe_webhook/", views.payment_stripe_webhook, name="payment_stripe_webhook"),

]
