from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class FriendShipPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'size'
    max_page_size = 20

    def get_paginated_response(self, friendships):
        return Response({
            'results': friendships,
            'page_number': self.page.number,
            'total_pages': self.page.paginator.num_pages,
            'total_results': self.page.paginator.count,
            'has_next_page': self.page.has_next(),
        })