from django.contrib import admin

from goods.models import Categories, Products, Rating

# admin.site.register(Categories)

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ["product", "user", "value"]
    
@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name',)}
    list_display = ["name"]


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ('name',)}
    list_display = ["name", "quantity", "price", "discount"]
    list_editable = ["discount"]
    search_fields = ["name", "description"]
    list_filter = ["quantity", "price", "discount", "category"]