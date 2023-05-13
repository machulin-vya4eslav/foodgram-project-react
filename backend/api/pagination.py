from rest_framework.pagination import PageNumberPagination


class CustomListPagination(PageNumberPagination):
    """
    Пагинация по параметру запроса limit.
    """

    page_size_query_param = 'limit'
