from django.core.management.base import BaseCommand
from faker import Faker

from ...models import SearchBarIndex


class FakeProject:
    def __init__(self):
        fake = Faker()
        self.id = fake.pyint()
        self.organization_name = fake.company()
        self.address = fake.address()
        self.affiliation = fake.pyint(min_value=1, max_value=10)
        self.partners = []
        for _ in range(fake.pyint(min_value=1, max_value=10)):
            self.partners.append(fake.pyint())

    def get_json(self):
        return self.__dict__


class FakeUser:
    def __init__(self):
        fake = Faker()
        self.name = fake.name()
        self.email = fake.email()


class FakeSearchableData:
    def __init__(self):
        fake = Faker()
        self.address = fake.address()
        self.email = fake.email()
        self.username = fake.name()
        self.phone = fake.phone_number()
        self.task_email = fake.email()

        self.affiliations = []
        for _ in range(fake.pyint(min_value=1, max_value=10)):
            self.affiliations.append(str(fake.pyint()))

        self.projects = []
        for _ in range(fake.pyint(min_value=1, max_value=10)):
            self.projects.append(FakeProject())

        self.users = []
        for _ in range(fake.pyint(min_value=1, max_value=10)):
            self.users.append(FakeUser())

    def get_affiliations(self):
        project_affiliations = []
        for project in self.projects:
            project_affiliations.append(str(project.affiliation))
        all_affiliations = self.affiliations + project_affiliations
        x = " ".join(all_affiliations)
        return x

    def get_project_ids(self):
        return " ".join(list(map(lambda x: str(x.id), self.projects)))

    def get_word_bag(self):
        word_bag = []
        word_bag.append(self.address)
        word_bag.append(self.email)
        word_bag.append(self.username)
        word_bag.append(self.phone)
        word_bag.append(self.task_email)
        project_words = list(
            map(lambda x: f"{x.organization_name} {x.address}", self.projects)
        )
        partners = list(map(lambda x: x.partners, self.projects))
        partner_words = [str(x) for partner_list in partners for x in partner_list]
        user_words = list(map(lambda x: f"{x.name} {x.email}", self.users))

        return " ".join(word_bag + project_words + partner_words + user_words)


class Command(BaseCommand):
    help = "Adds search indexes to the database"

    def handle(self, *args, **options):
        fake = Faker()

        types = ["partner", "participant"]

        for x in range(1):
            type = types[fake.pyint(min_value=0, max_value=len(types) - 1)]
            searchableData = FakeSearchableData()

            SearchBarIndex.objects.create(
                key=fake.pyint(),
                type=type,
                affiliations=searchableData.get_affiliations(),
                project_ids=searchableData.get_project_ids(),
                word_bag=searchableData.get_word_bag(),
            )
            print(f"Added search index #{x}")
