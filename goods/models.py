from django.db import models
from django.urls import reverse
from traitlets import default

from users.models import User

class Categories(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="URL")

    class Meta():
        db_table = 'category'
        verbose_name = "Категорию"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name
    
class Products(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name="URL")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    image = models.ImageField(upload_to='goods_images', blank=True, null=True, verbose_name="Изображение")
    price = models.DecimalField(default=0.00, max_digits=7, decimal_places=2, verbose_name="Цена")
    discount = models.DecimalField(default=0.00, max_digits=4, decimal_places=2, verbose_name="Скидка в процентах")
    quantity = models.PositiveIntegerField(default=0, verbose_name='Количество')
    category = models.ForeignKey(to=Categories, on_delete=models.CASCADE, verbose_name='Категория')
    average_rating = models.FloatField(default=0, verbose_name="Средний рейтинг")
    count_of_ratings = models.IntegerField(default=0, verbose_name="Количество оценок")

    class Meta():
        db_table = 'product'
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"
        ordering = ('id',)

    def __str__(self):
        return f"{self.name} Количество - {self.quantity}"
    
    def get_absolute_url(self):
        return reverse("catalog:product", kwargs={"slug": self.slug})

    def product_id(self):
        return f"{self.id:05}"
    
    
    def sell_price(self):
        if self.discount:
            return round(self.price - self.price * self.discount / 100, 2)
        return self.price
    
    def update_average_rating(self):
        rating_aggregation = Rating.objects.filter(product=self).aggregate(models.Avg("value"), models.Count("value"))
        avg_rating = rating_aggregation["value__avg"]
        count_of_ratings = rating_aggregation["value__count"]

        self.average_rating = avg_rating if avg_rating else 0
        self.count_of_ratings = count_of_ratings if count_of_ratings else 0
        self.save()

class Rating(models.Model):
    product = models.ForeignKey(to=Products, on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    value = models.IntegerField()
