from rest_framework import serializers
from .models import ThreatLog, BlockedIP

class ThreatLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThreatLog
        fields = '__all__'

class BlockedIPSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlockedIP
        fields = '__all__'
