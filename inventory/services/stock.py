from inventory.models import Stock
from stock.exceptions import InsufficientStockError, InvalidQuantityError

from .base import BaseService


class StockService(BaseService):
    @BaseService.atomic
    def issue_stock(self, stock: Stock, quantity: int, issued_by, issued_to=None):
        if quantity <= 0:
            raise InvalidQuantityError('Issue quantity must be greater than 0.')
        if not stock.can_issue(quantity):
            raise InsufficientStockError('Insufficient stock')

        stock.receive_quantity = 0
        stock.quantity = (stock.quantity or 0) - quantity
        stock.issue_quantity = quantity
        stock.issued_by = str(issued_by)
        stock.issued_by_user = issued_by
        stock.issued_to = str(issued_to) if issued_to else None
        stock.issued_to_person = issued_to
        stock.full_clean()
        stock.save()
        return stock

    @BaseService.atomic
    def receive_stock(self, stock: Stock, quantity: int, received_by):
        if quantity <= 0:
            raise InvalidQuantityError('Receive quantity must be greater than 0.')

        stock.issue_quantity = 0
        stock.quantity = (stock.quantity or 0) + quantity
        stock.receive_quantity = quantity
        stock.received_by = str(received_by)
        stock.received_by_user = received_by
        stock.full_clean()
        stock.save()
        return stock

    @BaseService.atomic
    def update_reorder_level(self, stock: Stock, reorder_level: int):
        if reorder_level < 0:
            raise InvalidQuantityError('Reorder level cannot be negative.')

        stock.re_order = reorder_level
        stock.full_clean()
        stock.save()
        return stock
