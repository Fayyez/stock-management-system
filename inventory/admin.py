from django.contrib import admin

from inventory.forms import StockCreateForm
from inventory.models import Category, Stock, StockHistory


class StockCreateAdmin(admin.ModelAdmin):
    list_display = ['category', 'item_name', 'quantity']
    form = StockCreateForm
    list_filter = ['category']
    search_fields = ['category', 'item_name']


admin.site.register(Stock, StockCreateAdmin)
admin.site.register(StockHistory)
admin.site.register(Category)
