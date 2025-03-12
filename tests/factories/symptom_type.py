import factory
import factory.fuzzy

from allergy.models import SymptomType
from tests.factories.user import UserFactory


class SymptomTypeFactory(factory.django.DjangoModelFactory[SymptomType]):
    class Meta:
        model = SymptomType

    name = factory.fuzzy.FuzzyText(length=10)
    user = factory.SubFactory(UserFactory)
