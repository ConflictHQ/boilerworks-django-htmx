from django.contrib import admin

from core.admin import BaseCoreAdmin

from .models import Product


@admin.register(Product)
class ProductAdmin(BaseCoreAdmin):
    list_display = ("name", "slug", "price", "sku", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "sku")
