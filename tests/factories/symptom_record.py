import factory
import factory.fuzzy

from allergy.models import SymptomRecord
from tests.factories.allergy_entry import AllergyEntryFactory
from tests.factories.symptom_type import SymptomTypeFactory


class SymptomRecordFactory(factory.django.DjangoModelFactory[SymptomRecord]):
    class Meta:
        model = SymptomRecord

    symptom_type = factory.SubFactory(SymptomTypeFactory, user=factory.SelfAttribute("..user"))
    intensity = factory.fuzzy.FuzzyInteger(1, 10)
    entry = factory.SubFactory(AllergyEntryFactory, user=factory.SelfAttribute("..user"))
