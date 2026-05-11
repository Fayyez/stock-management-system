from typing import List, Optional

from stock.models import Category

from .base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self):
        super().__init__(Category)

    def get_all(self) -> List[Category]:
        return list(self.model.objects.all())

    def get_by_id(self, pk) -> Optional[Category]:
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs) -> Category:
        record = self.model(**kwargs)
        record.full_clean()
        record.save()
        return record

    def update(self, pk, **kwargs) -> Optional[Category]:
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
