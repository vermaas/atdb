import logging
from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.response import Response
from django_filters import rest_framework as filters
from django.template import loader
from django.shortcuts import render, redirect

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

class StatusDetailsView(generics.RetrieveUpdateDestroyAPIView):
    model = Status
    queryset = Status.objects.all()
    serializer_class = StatusSerializer

# ex: /atdb/dataproducts?status__in=created,archived
class DataProductFilter(filters.FilterSet):

    class Meta:
        model = DataProduct

        fields = {
            'dataproduct_type': ['exact', 'in'],  # ../dataproducts?dataProductType=IMAGE,VISIBILITY
            'description': ['exact', 'icontains'],
            'name': ['exact', 'icontains'],
            'filename': ['exact', 'icontains'],
            'taskID': ['exact', 'icontains'],
            'creationTime': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'generatedByObservation__taskID': ['exact', 'in', 'icontains'],
            'my_status': ['exact', 'icontains'],
            'my_locations': ['exact', 'icontains'],
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
            'my_status': ['exact', 'icontains'],
            'taskID': ['exact', 'icontains'],
            'creationTime': ['gt', 'lt', 'gte', 'lte', 'contains', 'exact'],
            'my_locations': ['exact', 'icontains'],
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


class ObservationValidateView(generics.UpdateAPIView):
    model = Observation
    queryset = Observation.objects.all()

    def get(self, request, pk, format=None):
        observation = self.get_object()
        observation.new_status = 'valid'
        observation.save()
        return redirect('/atdb/')


def BasicObservationValidateView(request,pk):
    model = Observation
    observation = Observation.objects.get(pk=pk)
    observation.new_status = 'valid'
    observation.save()

    return redirect('/atdb/')


# set the status of all dataproducts if this observation to 'new_status'
def ObservationSetStatusDataProducts(request,pk,new_status):
    model = Observation
    observation = Observation.objects.get(pk=pk)
    taskID = observation.taskID

    dataproducts = DataProduct.objects.filter(taskID=taskID)
    for dataproduct in dataproducts:
        dataproduct.new_status = new_status
        dataproduct.save()

    return redirect('/atdb/')

class DataProductValidateView(generics.UpdateAPIView):
    model = DataProduct
    queryset = DataProduct.objects.all()
    serializer_class = DataProductSerializer

    def get(self, request, pk, format=None):
        dataproduct = self.get_object()
        dataproduct.new_status = 'valid'
        dataproduct.save()
        return redirect('/atdb/')


def DataProductSetStatusView(request,pk,new_status):
    model = DataProduct
    dataproduct = DataProduct.objects.get(pk=pk)
    dataproduct.new_status = new_status
    dataproduct.save()

    return redirect('/atdb/')