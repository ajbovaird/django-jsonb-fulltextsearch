from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.views.decorators.cache import cache_page
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Q

from .models import SearchBarIndex


class ResultViewModel:
    def __init__(self, id, type, affiliations, project_ids, word_bag):
        self.id = id
        self.type = type
        self.affiliations = affiliations
        self.project_ids = project_ids
        self.word_bag = word_bag


@method_decorator(cache_page(60 * 5), name="dispatch")
class SearchBarIndexList(ListView):
    model = SearchBarIndex
    context_object_name = "search_results"
    template_name = "search.html"


class SearchResultsList(ListView):
    model = SearchBarIndex
    context_object_name = "search_results"
    template_name = "search_results.html"

    def get_queryset(self):
        query = self.request.GET.get("q")

        input_terms = query.split(" ")
        search_terms = ""

        # Get the search_terms formatted so they can be used in the search query.
        # Append each tearm with ':* ' to make it a prefix search.
        # If it isn't the last search term, append '& ' to make it a AND search.
        input_terms_count = len(input_terms)
        for i in range(input_terms_count):
            search_terms = f"{search_terms}{input_terms[i]}:* "
            if i != input_terms_count - 1:
                search_terms = f"{search_terms}& "
        print(search_terms)
        # setup the actual query, using the raw search type which allows us to search prefixes wiht ":*"
        query = SearchQuery(search_terms, search_type="raw", config="simple")

        # add the calculated rank field to the SELECT statement
        rank = SearchRank(F("project_ids_search_vector"), query)
        results = (
            SearchBarIndex.objects.annotate(rank=rank)
            .filter(
                Q(word_bag_search_vector=query) | Q(project_ids_search_vector=query)
            )
            .order_by("-rank")
        )

        print(results.query)
        return [
            ResultViewModel(
                result.id,
                result.type,
                result.affiliations,
                result.project_ids,
                result.word_bag,
            )
            for result in results
        ]
