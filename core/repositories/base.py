from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

from django.db import models

T = TypeVar('T', bound=models.Model)


class BaseRepository(ABC, Generic[T]):
    def __init__(self, model_class):
        self.model = model_class

    @abstractmethod
    def get_all(self) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, pk) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def create(self, **kwargs) -> T:
        raise NotImplementedError

    @abstractmethod
    def update(self, pk, **kwargs) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, pk) -> bool:
        raise NotImplementedError
