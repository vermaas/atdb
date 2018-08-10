from rest_framework import serializers
from .models import DataProduct

class DataProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = DataProduct
        fields = '__all__'