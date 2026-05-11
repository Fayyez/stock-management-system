from django.core.exceptions import ValidationError

from stock.models import Stock
from stock.repositories import StockRepository

from .base import BaseService


class StockService(BaseService):
    def __init__(self, repo=None):
        self.repo = repo or StockRepository()

    def get_stock_or_raise(self, stock_id):
        stock = self.repo.get_by_id(stock_id)
        if not stock:
            raise ValidationError(f'Stock with id {stock_id} was not found.')
        return stock

    @BaseService.atomic
    def issue_stock(self, stock: Stock, quantity: int, issued_by):
        if quantity <= 0:
            raise ValidationError('Issue quantity must be greater than 0.')
        if not stock.can_issue(quantity):
            raise ValidationError('Insufficient stock')

        stock.receive_quantity = 0
        stock.quantity = (stock.quantity or 0) - quantity
        stock.issue_quantity = quantity
        stock.issued_by = str(issued_by)
        stock.full_clean()
        stock.save()
        return stock

    @BaseService.atomic
    def receive_stock(self, stock: Stock, quantity: int, received_by):
        if quantity <= 0:
            raise ValidationError('Receive quantity must be greater than 0.')

        stock.issue_quantity = 0
        stock.quantity = (stock.quantity or 0) + quantity
        stock.receive_quantity = quantity
        stock.received_by = str(received_by)
        stock.full_clean()
        stock.save()
        return stock

    @BaseService.atomic
    def update_reorder_level(self, stock: Stock, reorder_level: int):
        if reorder_level < 0:
            raise ValidationError('Reorder level cannot be negative.')

        stock.re_order = reorder_level
        stock.full_clean()
        stock.save()
        return stock
