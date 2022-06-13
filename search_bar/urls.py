from django.urls import path

from .views import SearchBarIndexList, SearchResultsList

urlpatterns = [
    path("", SearchBarIndexList.as_view(), name="all_search_indexes"),
    path("search/", SearchResultsList.as_view(), name="search_results"),
]