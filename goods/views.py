from django.core.paginator import Paginator
from django.shortcuts import render

from goods.models import Products, Rating
from goods.utils import q_search
from orders.models import OrderItem


def catalog(request, category_slug=None):

    page = request.GET.get('page', 1)
    on_sale = request.GET.get('on_sale', None)
    order_by = request.GET.get('order_by', None)
    query = request.GET.get('q', None)
    price_start = request.GET.get("price_start", None)
    price_end = request.GET.get("price_end", None)


    if category_slug == "all":
        goods = Products.objects.all()
    elif query:
        goods = q_search(query=query)
    else:
        goods = Products.objects.filter(category__slug=category_slug)

    if on_sale:
        goods = goods.filter(discount__gt=0)

    if price_start or price_end:
        if price_start and price_end:
            goods = goods.filter(price__gte=price_start).filter(price__lte=price_end)

    if order_by and order_by != 'default':
        goods = goods.order_by(order_by)
    


    paginator = Paginator(goods, 6)
    current_page = paginator.page(int(page))   

    context = {
        'title': 'Home - Каталог',
        'goods': current_page,
        'slug_url': category_slug,
    }
    return render(request, 'goods/catalog.html', context=context)


def product(request, slug):
    product = Products.objects.get(slug=slug)
    if request.user.is_authenticated:
        if request.method == "POST":
            value = int(request.POST.get("star"))
            rating = Rating.objects.create(product=product, value=value, user=request.user)
            product.update_average_rating()
        avg_rating = product.average_rating
        # count_of_ratings = product.count_of_ratings
        
        user_rating = Rating.objects.filter(user=request.user, product=product)

        order_item = OrderItem.objects.filter(product=product, order__is_paid=True).order_by("-id").first()

        context = {
            'product': product,
            "avg_rating": round(avg_rating, 2),
            # "count_of_ratings": count_of_ratings,
            "user_rating": user_rating,
            "order_item": order_item,
        }
    else:
        context = {
            'product': product,
            "avg_rating": round(product.average_rating, 2),
        }

    return render(request, 'goods/product.html', context=context)