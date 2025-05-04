from rest_framework import serializers
from .models import TrendData

class TrendDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrendData
        fields = '__all__'

