from django.shortcuts import render


def create_order(request):
    context = {
        "title": "HOME - Оплата",
        "margin-left": "",
    }
    return render(request, "orders/create_order.html")