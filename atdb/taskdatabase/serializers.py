from rest_framework import serializers
from .models import DataProduct, Observation, Location, Status, StatusType


#class LocationSerializer(serializers.ModelSerializer):
#
#    class Meta:
#        model = Location
#        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):

    class Meta:

        model = Location
        fields = ('id','host','path','timestamp')


class StatusTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = StatusType
        fields = '__all__'


class StatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = Status
        fields = '__all__'



class DataProductSerializer(serializers.ModelSerializer):

    locations = serializers.HyperlinkedRelatedField(
        label='Locations',
        many=True,
        queryset = Location.objects.all(),
        view_name='location-detail-view',
        lookup_field='pk',
        required=True)

#    locations = LocationSerializer(
#         many=True,
#         required=True)

    status = serializers.HyperlinkedRelatedField(
        many=False,
        queryset = Status.objects.all(),
        view_name='status-detail-view',
        required=True)

    statusHistory = serializers.SlugRelatedField(
        label='History',
        many=True,
        queryset = Status.objects.all(),
        slug_field='derived_name',
        required=True)

    #status = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = DataProduct
        fields = ('id','filename','description','type','taskID','creationTime','size','quality',
                  'locations','status','current_status','statusHistory')


class ObservationSerializer(serializers.ModelSerializer):
    generatedDataProducts = serializers.HyperlinkedRelatedField(
        label='DataProducts',
        many=True,
        queryset = DataProduct.objects.all(),
        view_name='dataproduct-detail-view',
        lookup_field='pk',
        required=True)

    locations = serializers.HyperlinkedRelatedField(
        label='Locations',
        many=True,
        queryset = Location.objects.all(),
        view_name='location-detail-view',
        lookup_field='pk',
        required=True)

    status = serializers.HyperlinkedRelatedField(
        many=False,
        queryset = Status.objects.all(),
        view_name='status-detail-view',
        required=True)

    statusHistory = serializers.SlugRelatedField(
        label='History',
        many=True,
        queryset = Status.objects.all(),
        slug_field='derived_name',
        required=True)

    class Meta:
        model = Observation
        fields = ('id', 'name', 'process_type','taskID','creationTime',
                  'generatedDataProducts','locations','status','current_status','statusHistory')