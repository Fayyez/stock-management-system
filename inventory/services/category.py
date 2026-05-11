from inventory.repositories import category_repo


class CategoryService:
    def __init__(self, repo=None):
        self.repo = repo or category_repo

    def list_categories(self):
        return self.repo.get_all()

    def search_categories(self, name=''):
        return self.repo.search(name=name)
