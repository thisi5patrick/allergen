import factory
import factory.fuzzy

from allergy.models import AllergySymptoms
from tests.factories.allergy_entries import AllergyEntriesFactory


class AllergySymptomsFactory(factory.django.DjangoModelFactory[AllergySymptoms]):
    class Meta:
        model = AllergySymptoms

    symptom = factory.fuzzy.FuzzyChoice(AllergySymptoms.Symptoms)
    entry = factory.SubFactory(AllergyEntriesFactory)
