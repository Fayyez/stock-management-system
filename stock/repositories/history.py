from typing import List, Optional

from stock.models import StockHistory

from .base import BaseRepository


class StockHistoryRepository(BaseRepository[StockHistory]):
    def __init__(self):
        super().__init__(StockHistory)

    def get_all(self) -> List[StockHistory]:
        return list(self.model.objects.all())

    def get_by_id(self, pk) -> Optional[StockHistory]:
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def search(self, item_name: str = '', category_id: Optional[int] = None, start_date=None, end_date=None) -> List[StockHistory]:
        queryset = self.model.objects.all()
        if item_name:
            queryset = queryset.filter(item_name__icontains=item_name)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if start_date and end_date:
            queryset = queryset.filter(last_updated__range=[start_date, end_date])
        return list(queryset)

    def create(self, **kwargs) -> StockHistory:
        record = self.model(**kwargs)
        record.full_clean()
        record.save()
        return record

    def update(self, pk, **kwargs) -> Optional[StockHistory]:
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
