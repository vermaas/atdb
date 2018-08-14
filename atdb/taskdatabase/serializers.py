from rest_framework import serializers
from .models import DataProduct, Observation, Location, Status


#class LocationSerializer(serializers.ModelSerializer):
#
#    class Meta:
#        model = Location
#        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ('id','location','timestamp')


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = ('id','name','timestamp')



class DataProductSerializer(serializers.ModelSerializer):
    # this adds a 'parent_observation' list with hyperlinks to the DataProduct API.
    # note that 'generatedByObservation' is not defined in the DataProduct model, but in the Observation model.
    generatedByObservation = serializers.HyperlinkedRelatedField(
        many=True,
        # read_only=True,
        queryset=Observation.objects.all(),
        view_name='observation-detail-view',
        required=False,
        lookup_field='pk'
    )

    locations = serializers.HyperlinkedRelatedField(
        label='Locations',
        many=True,
        queryset = Location.objects.all(),
        view_name='location-detail-view',
        lookup_field='pk',
        required=False)

#    locations = LocationSerializer(
#         many=True,
#         required=True)

    statusHistory = StatusSerializer(
         many=True,
         required=False,
         read_only=True)

#    statusHistory = serializers.HyperlinkedRelatedField(
#        label='History',
#        many=True,
#        queryset = Status.objects.all(),
#        view_name='status-detail-view',
#        # slug_field='my_status',
#        required=False)


    class Meta:
        model = DataProduct
        fields = ('id','task_type','name','filename','description','dataproduct_type',
                  'taskID','creationTime','size','quality',
                  'locations','my_locations','my_status','new_status','statusHistory','generatedByObservation',
                  'new_location')


class ObservationSerializer(serializers.ModelSerializer):
    generatedDataProducts = serializers.HyperlinkedRelatedField(
        label='DataProducts',
        many=True,
        queryset = DataProduct.objects.all(),
        view_name='dataproduct-detail-view',
        lookup_field='pk',
        required=False)

    locations = serializers.HyperlinkedRelatedField(
        label='Locations',
        many=True,
        queryset = Location.objects.all(),
        view_name='location-detail-view',
        lookup_field='pk',
        required=False)

    statusHistory = StatusSerializer(
         many=True,
         required=False)

    class Meta:
        model = Observation
        fields = ('id','task_type', 'name', 'process_type','taskID','creationTime',
                  'new_location','locations','my_locations','my_status','new_status','statusHistory','generatedDataProducts')