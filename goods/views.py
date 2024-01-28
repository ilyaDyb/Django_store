from django.shortcuts import render

from goods.models import Products


def catalog(request):

    goods = Products.objects.all()

    context = {
        'title': 'Home - Каталог',
        'goods': goods,
    }
    return render(request, 'goods/catalog.html', context=context)


def product(request, slug):
    product = Products.objects.get(slug=slug)
    context = {
        'product': product
    }
    return render(request, 'goods/product.html', context=context)