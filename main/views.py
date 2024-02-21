from django.shortcuts import render

from goods.models import Categories

# Create your views here.
def index(request):

    categories = Categories.objects.all()

    context = {
        'title': "HOME - Главная",
        'content': "Магазин, который вы искали",
        'categories': categories
    }

    return render(request, "main/index.html", context=context)


def about(request):
    context = {
        'title': "Home - О нас",
        'content': "О нас",
        'text_on_page': 'Текст о том почему этот магазин такой классный'
    }

    return render(request, "main/about.html", context=context)