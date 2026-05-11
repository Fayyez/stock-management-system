from .category import CategoryRepository
from .history import StockHistoryRepository
from .person import PersonRepository
from .stock import StockRepository


class RepositoryFactory:
    _repositories = {
        'stock': StockRepository,
        'category': CategoryRepository,
        'person': PersonRepository,
        'history': StockHistoryRepository,
    }

    @classmethod
    def get_repository(cls, name: str):
        repository = cls._repositories.get(name)
        if not repository:
            raise ValueError(f'Unknown repository: {name}')
        return repository()


stock_repo = StockRepository()
category_repo = CategoryRepository()
person_repo = PersonRepository()
history_repo = StockHistoryRepository()
