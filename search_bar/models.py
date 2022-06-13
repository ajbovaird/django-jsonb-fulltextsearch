from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.db import models
from django.db.models import F


class SearchBarIndex(models.Model):
    key = models.IntegerField()
    type = models.TextField()
    affiliations = models.TextField()
    project_ids = models.TextField()
    word_bag = models.TextField()
    word_bag_search_vector = SearchVectorField(null=True)
    affiliations_search_vector = SearchVectorField(null=True)
    project_ids_search_vector = SearchVectorField(null=True)

    class Meta:
        indexes = [
            GinIndex(
                fields=[
                    "project_ids_search_vector",
                    "affiliations_search_vector",
                    "word_bag_search_vector",
                ],
                name="search_bar_gin_index",
            ),
        ]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        SearchBarIndex.objects.annotate(
            word_bag_search_vector_name=SearchVector("word_bag", config="simple"),
            affiliations_search_vector_name=SearchVector("affiliations"),
            project_ids_search_vector_name=SearchVector("project_ids", weight="A"),
        ).filter(id=self.id).update(
            word_bag_search_vector=F("word_bag_search_vector_name"),
            affiliations_search_vector=F("affiliations_search_vector_name"),
            project_ids_search_vector=F("project_ids_search_vector_name"),
        )

    def __str__(self):
        return f"type: {self.type}, key: {self.key}"
