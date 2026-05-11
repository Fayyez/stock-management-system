from django.test import SimpleTestCase

from inventory.services.stock import StockService
from stock.exceptions import InsufficientStockError


class DummyStock:
    def __init__(self, quantity=10, issue_quantity=0, receive_quantity=0, re_order=5):
        self.quantity = quantity
        self.issue_quantity = issue_quantity
        self.receive_quantity = receive_quantity
        self.re_order = re_order
        self.issued_by = ''
        self.received_by = ''
        self.issued_by_user = None
        self.received_by_user = None
        self.issued_to = ''
        self.issued_to_person = None

    def can_issue(self, quantity):
        return self.quantity >= quantity

    def full_clean(self):
        return None

    def save(self):
        return None


class StockServiceTestCase(SimpleTestCase):
    def setUp(self):
        self.service = StockService()

    def test_issue_stock_success(self):
        stock = DummyStock(quantity=10)
        recipient = object()
        updated = self.service.issue_stock(stock=stock, quantity=4, issued_by='tester', issued_to=recipient)

        self.assertEqual(updated.quantity, 6)
        self.assertEqual(updated.issue_quantity, 4)
        self.assertEqual(updated.receive_quantity, 0)
        self.assertIs(updated.issued_to_person, recipient)

    def test_issue_stock_insufficient(self):
        stock = DummyStock(quantity=2)

        with self.assertRaises(InsufficientStockError):
            self.service.issue_stock(stock=stock, quantity=4, issued_by='tester', issued_to=None)

    def test_receive_stock_success(self):
        stock = DummyStock(quantity=5)
        updated = self.service.receive_stock(stock=stock, quantity=3, received_by='tester')

        self.assertEqual(updated.quantity, 8)
        self.assertEqual(updated.receive_quantity, 3)
        self.assertEqual(updated.issue_quantity, 0)
