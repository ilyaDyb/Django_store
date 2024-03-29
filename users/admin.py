from django.contrib import admin
from carts.admin import CartTabAdmin
from orders.admin import OrderTabularAdmin


from users.models import User
# Register your models here.

# admin.site.register(User)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["id", "username", "first_name", "last_name", "email"]
    search_fields = ["id", "username", "first_name", "last_name", "email"]

    inlines = [CartTabAdmin, OrderTabularAdmin]