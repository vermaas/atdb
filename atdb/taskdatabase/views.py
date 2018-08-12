import logging
from django.http import HttpResponse
from rest_framework import generics
from django_filters import rest_framework as filters
from django.template import loader
from django.shortcuts import render

from .models import DataProduct, Observation, Location, Status
from .serializers import DataProductSerializer, ObservationSerializer, LocationSerializer, StatusSerializer

datetime_format_string = '%Y-%m-%dT%H:%M:%SZ'

logger = logging.getLogger(__name__)

# http://localhost:8000/atdb/
def index(request):

    latest_observations_list = Observation.objects.order_by('-creationTime')[:50]
    latest_dataproducts_list = DataProduct.objects.order_by('-creationTime')[:50]
    context = {
        'latest_observations_list': latest_observations_list,
        'latest_dataproducts_list': latest_dataproducts_list
        }
    return render(request, 'taskdatabase/index.html', context)


def detail(request, dataproduct_id):
    return HttpResponse("You're looking at dataproduct %s." % dataproduct_id)


# --- class based views ---
class LocationListView(generics.ListCreateAPIView):
    model = Location
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

# ex: /atdb/dataproducts/5/
class LocationDetailsView(generics.RetrieveUpdateDestroyAPIView):
    model = Location
    queryset = Location.objects.all()
    serializer_class = LocationSerializer

class StatusListView(generics.ListCreateAPIView):
    model = Status
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

# ex: /atdb/dataproducts/5/
class StatusDetailsView(generics.RetrieveUpdateDestroyAPIView):
    model = Status
    queryset = Status.objects.all()
    serializer_class = StatusSerializer
    
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