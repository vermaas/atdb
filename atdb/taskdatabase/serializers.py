from rest_framework import serializers
from .models import DataProduct, Observation

class DataProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataProduct
        fields = '__all__'

class ObservationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Observation
        fields = '__all__'