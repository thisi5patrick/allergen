from datetime import date

import factory

from allergy.models import AllergyEntries
from tests.factories.user import UserFactory


class AllergyEntriesFactory(factory.django.DjangoModelFactory[AllergyEntries]):
    class Meta:
        model = AllergyEntries

    entry_date = factory.LazyFunction(lambda: date.today())
    user = factory.SubFactory(UserFactory)
