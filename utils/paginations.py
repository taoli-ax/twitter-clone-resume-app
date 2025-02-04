from django.db.models import QuerySet
from rest_framework.pagination import BasePagination
from rest_framework.response import Response
from dateutil import parser

class EndlessPagination(BasePagination):
    page_size = 10

    def __init__(self):
        super(EndlessPagination, self).__init__()
        self.has_next_page = False

    def paginate_ordered_list(self, reversed_ordered_list, request):
        if 'created_at_gt' in request.query_params:
            create_at_gt = parser.isoparse(request.query_params['created_at_gt'])
            objects = []
            for item in reversed_ordered_list:
                if item.created_at > create_at_gt:
                    objects.append(item)
                else:
                    break
            self.has_next_page = False
            return objects
        index = 0
        if 'created_at_lt' in request.query_params:
            create_at_lt = parser.isoparse(request.query_params['created_at_lt'])
            for index, obj in enumerate(reversed_ordered_list):
                # 倒序的列表，出现第一个符合条件的index,obj,就break
                if obj.created_at < create_at_lt:
                   break
            else:
                reversed_ordered_list = []
        self.has_next_page = len(reversed_ordered_list)> index + self.page_size
        return reversed_ordered_list[index: index + self.page_size]



    def paginate_queryset(self, queryset, request, view=None):
        if type(queryset) == list:
            return self.paginate_ordered_list(queryset, request)
        if 'created_at_gt' in request.query_params:
            # 如果要更新所有数据，
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