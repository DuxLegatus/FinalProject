from rest_framework.pagination import LimitOffsetPagination

class PaginationLimitOffset(LimitOffsetPagination):
    default_limit = 30
    max_limit = 50