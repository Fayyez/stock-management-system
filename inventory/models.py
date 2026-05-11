from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class StockBaseModel(models.Model):
    category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=True, null=True)
    item_name = models.CharField(max_length=50, blank=True, null=True)
    quantity = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    receive_quantity = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    received_by = models.CharField(max_length=50, blank=True, null=True)
    received_by_user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='stock_received_transactions')
    issue_quantity = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])
    issued_by = models.CharField(max_length=50, blank=True, null=True)
    issued_by_user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, blank=True, null=True, related_name='stock_issued_transactions')
    issued_to = models.CharField(max_length=50, blank=True, null=True)
    issued_to_person = models.ForeignKey('core.Person', on_delete=models.SET_NULL, blank=True, null=True, related_name='stock_received_items')
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.CharField(max_length=50, blank=True, null=True)
    re_order = models.IntegerField(default=0, blank=True, null=True, validators=[MinValueValidator(0)])

    class Meta:
        abstract = True


class Category(models.Model):
    group = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'stock_category'
        managed = False

    def __str__(self):
        return self.group


class Stock(StockBaseModel):
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)
    date = models.DateTimeField(auto_now_add=False, auto_now=False, default=timezone.now)
    export_to_csv = models.BooleanField(default=False)
    image = models.ImageField(upload_to='stock/images', null=True, blank=True)

    class Meta:
        db_table = 'stock_stock'
        managed = False
        indexes = [
            models.Index(fields=['item_name']),
            models.Index(fields=['category']),
            models.Index(fields=['last_updated']),
        ]

    def __str__(self):
        return self.item_name + ' ' + str(self.quantity) + ' ' + str(self.last_updated)

    def can_issue(self, quantity):
        return (self.quantity or 0) >= quantity

    def clean(self):
        super().clean()
        for field in ('quantity', 'receive_quantity', 'issue_quantity', 're_order'):
            value = getattr(self, field) or 0
            if value < 0:
                raise ValidationError({field: 'Value cannot be negative.'})


class StockHistory(StockBaseModel):
    last_updated = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)
    timestamp = models.DateTimeField(auto_now_add=False, auto_now=False, null=True)

    class Meta:
        db_table = 'stock_stockhistory'
        managed = False
        ordering = ['-timestamp']
        verbose_name_plural = 'Stock Histories'
        indexes = [
            models.Index(fields=['item_name']),
            models.Index(fields=['timestamp']),
        ]
