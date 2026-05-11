from core.repositories import person_repo


class PersonService:
    def __init__(self, repo=None):
        self.repo = repo or person_repo

    def list_people(self):
        return self.repo.get_all()

    def search_people(self, name=''):
        return self.repo.search(name=name)
