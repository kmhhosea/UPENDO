from django.contrib import admin

from .models import Category, Transaction


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category_type", "is_active")
    list_filter = ("category_type", "is_active")
    search_fields = ("name", "user__username")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "transaction_type", "category", "amount", "transaction_date", "created_at")
    list_filter = ("transaction_type", "transaction_date")
    search_fields = ("description", "user__username", "category__name")
