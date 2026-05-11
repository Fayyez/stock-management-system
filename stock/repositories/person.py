from typing import List, Optional

from stock.models import Person

from .base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    def __init__(self):
        super().__init__(Person)

    def get_all(self) -> List[Person]:
        return list(self.model.objects.all())

    def get_by_id(self, pk) -> Optional[Person]:
        try:
            return self.model.objects.get(pk=pk)
        except self.model.DoesNotExist:
            return None

    def create(self, **kwargs) -> Person:
        record = self.model(**kwargs)
        record.full_clean()
        record.save()
        return record

    def update(self, pk, **kwargs) -> Optional[Person]:
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
