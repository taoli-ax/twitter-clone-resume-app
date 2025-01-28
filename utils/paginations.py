from rest_framework.pagination import BasePagination
from rest_framework.response import Response

class EndlessPagination(BasePagination):
    page_size = 10

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def paginate_queryset(self, queryset, request, view=None):
        if 'created_at_gt' in request.query_params:
            # 如果要更新所有数据，就查询created_at大于第一条推特的内容
            create_at_gt = request.query_params.get('created_at_gt')
            queryset = queryset.filter(created_at__gt=create_at_gt)
            self.has_next_page = False
            return queryset.order_by('-created_at')
        if 'created_at_lt' in request.query_params:
            created_at_lt = request.query_params['created_at_lt']
            queryset = queryset.filter(created_at__lt=created_at_lt)

        queryset = queryset.order_by('-created_at')[:self.page_size+1]
        self.has_next_page = len(queryset) > self.page_size
        return queryset[:self.page_size]

    def get_paginated_response(self, data):
        return Response({
            'has_next_page':self.has_next_page,
            'results':data
        })