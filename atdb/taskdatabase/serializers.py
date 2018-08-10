from rest_framework import serializers
from .models import DataProduct, Observation, Location, Status, StatusType


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'


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

    #status = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = DataProduct
        fields = ('id','filename','description','type','taskID','creationTime','size','quality','locations')


class ObservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Observation
        fields = '__all__'