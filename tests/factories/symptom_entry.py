from datetime import date

import factory
import factory.fuzzy

from allergy.models import SymptomEntry
from tests.factories.symptom_type import SymptomTypeFactory
from tests.factories.user import UserFactory


class SymptomEntryFactory(factory.django.DjangoModelFactory[SymptomEntry]):
    class Meta:
        model = SymptomEntry

    user = factory.SubFactory(UserFactory)
    entry_date = factory.LazyFunction(lambda: date.today())
    intensity = factory.fuzzy.FuzzyInteger(1, 10)
    symptom_type = factory.SubFactory(SymptomTypeFactory, user=factory.SelfAttribute("..user"))
