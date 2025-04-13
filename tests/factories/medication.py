import factory
import factory.fuzzy

from allergy.models import Medication
from tests.factories.user import UserFactory


class MedicationFactory(factory.django.DjangoModelFactory[Medication]):
    class Meta:
        model = Medication

    user = factory.SubFactory(UserFactory)
    medication_name = factory.Sequence(lambda n: f"Medication {n}")
    medication_type = factory.fuzzy.FuzzyChoice([choice[0] for choice in Medication.MedicationType.choices])
