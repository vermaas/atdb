from django.http import HttpResponse
from rest_framework import generics
from django_filters import rest_framework as filters

from .models import DataProduct
from .serializers import DataProductSerializer

from django.views.generic import ListView, DetailView

def index_basic1(request):
    return HttpResponse("Welcome to ATDB.")

# http://localhost:8000/atdb/
def index(request):
    latest_dataproducts_list = DataProduct.objects.order_by('-creationTime')[:5]
    output = ', '.join([dp.taskId for dp in latest_dataproducts_list])
    return HttpResponse(output)

def detail(request, dataproduct_id):
    return HttpResponse("You're looking at dataproduct %s." % dataproduct_id)


# --- class based views ---
# ex: /atdb/dataproducts?status__in=created,archived
class DataProductFilter(filters.FilterSet):

    class Meta:
        model = DataProduct

        fields = {
            'type': ['exact', 'in'],  # ../dataproducts?dataProductType=IMAGE,VISIBILITY
            'description': ['exact', 'icontains'],
            'taskId': ['exact', 'icontains'],
            'creationTime': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact']
        }


# ex: /atdb/dataproducts/
class DataProductListView(generics.ListCreateAPIView):
    model = DataProduct
    queryset = DataProduct.objects.all()
    serializer_class = DataProductSerializer

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = DataProductFilter


# ex: /atdb/dataproducts/5/
class DataProductDetailsView(generics.RetrieveUpdateDestroyAPIView):
    model = DataProduct
    queryset = DataProduct.objects.all()
    serializer_class = DataProductSerializer