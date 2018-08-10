from django.http import HttpResponse
from rest_framework import generics
from django_filters import rest_framework as filters

from .models import DataProduct, Observation, Location, Status
from .serializers import DataProductSerializer, ObservationSerializer, LocationSerializer, StatusSerializer

from django.views.generic import ListView, DetailView

# http://localhost:8000/atdb/
def index(request):
    latest_dataproducts_list = DataProduct.objects.order_by('-creationTime')[:5]
    output = ', '.join([dp.taskID for dp in latest_dataproducts_list])
    return HttpResponse(output)

def detail(request, dataproduct_id):
    return HttpResponse("You're looking at dataproduct %s." % dataproduct_id)


# --- class based views ---
# ex: /atdb/dataproducts/
class LocationListView(generics.ListCreateAPIView):
    model = Location
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

# ex: /atdb/dataproducts/5/
class LocationDetailsView(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

# ex: /atdb/dataproducts?status__in=created,archived
class DataProductFilter(filters.FilterSet):

    class Meta:
        model = DataProduct

        fields = {
            'type': ['exact', 'in'],  # ../dataproducts?dataProductType=IMAGE,VISIBILITY
            'description': ['exact', 'icontains'],
            'taskID': ['exact', 'icontains'],
            'creationTime': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'generatedByObservation__taskID': ['exact', 'in', 'icontains'],
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


class ObservationFilter(filters.FilterSet):

    class Meta:
        model = Observation

        fields = {
            'process_type': ['exact', 'in'],
            'name': ['exact', 'icontains'],
            'taskID': ['exact', 'icontains'],
            'creationTime': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact']
        }


# ex: /atdb/observations/
class ObservationListView(generics.ListCreateAPIView):
    model = Observation
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer

    # using the Django Filter Backend - https://django-filter.readthedocs.io/en/latest/index.html
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ObservationFilter


# ex: /atdb/observations/5/
class ObservationDetailsView(generics.RetrieveUpdateDestroyAPIView):
    model = Observation
    queryset = Observation.objects.all()
    serializer_class = ObservationSerializer