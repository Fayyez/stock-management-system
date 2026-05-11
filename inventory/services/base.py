from abc import ABC

from django.db import transaction


class BaseService(ABC):
    @staticmethod
    def atomic(func):
        def wrapper(*args, **kwargs):
            with transaction.atomic():
                return func(*args, **kwargs)
        return wrapper
