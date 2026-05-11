from typing import List, Optional

from django.db.models import F

from inventory.models import Stock

from .base import BaseRepository


class StockRepository(BaseRepository[Stock]):
    def __init__(self):
        super().__init__(Stock)

    def get_all(self) -> List[Stock]:
        return list(self.model.objects.all())

    def get_by_id(self, pk) -> Optional[Stock]:
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def search(self, item_name: str = '', category_id: Optional[int] = None) -> List[Stock]:
        queryset = self.model.objects.all()
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return list(queryset)

    def get_below_reorder_level(self) -> List[Stock]:
        return list(self.model.objects.filter(quantity__lte=F('re_order')))

    def create(self, **kwargs) -> Stock:
        record = self.model(**kwargs)
        record.full_clean()
        record.save()
        return record

    def update(self, pk, **kwargs) -> Optional[Stock]:
        record = self.get_by_id(pk)
        if not record:
            return None
        for key, value in kwargs.items():
            setattr(record, key, value)
        record.full_clean()
        record.save()
        return record

    def delete(self, pk) -> bool:
        record = self.get_by_id(pk)
        if not record:
            return False
        record.delete()
        return True
