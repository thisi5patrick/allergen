from datetime import date

import factory

from allergy.models import AllergyEntry
from tests.factories.user import UserFactory


class AllergyEntryFactory(factory.django.DjangoModelFactory[AllergyEntry]):
    class Meta:
        model = AllergyEntry

    entry_date = factory.LazyFunction(lambda: date.today())
    user = factory.SubFactory(UserFactory)
