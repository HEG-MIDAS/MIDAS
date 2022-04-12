from rest_framework import serializers

class StatusSerializer(serializers.Serializer):
    """
    It's the status serializer
    """
    status = serializers.CharField(max_length=200)