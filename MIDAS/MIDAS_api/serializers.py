from rest_framework import serializers
from MIDAS_app.models import Source, Station, Parameter, ParametersOfStation

class StatusSerializer(serializers.Serializer):
    """
    It's the status serializer
    """
    status = serializers.CharField(max_length=200)

class SourceSerializer(serializers.ModelSerializer):
    # Retrieve Stations by Name (or any value added in slug_field)
    # To retrieve by id, use PrimaryKeyRelatedField
    station = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Source.objects.all())

    class Meta:
        model = Source
        fields = ['id','name','slug','url','infos','station']
        lookup_field = 'slug'

class StationSerializer(serializers.ModelSerializer):
    # Display Namr rather than id
    source = serializers.ReadOnlyField(source='source.name')
    parameters_of_station = serializers.PrimaryKeyRelatedField(many=True, queryset=ParametersOfStation.objects.all())
    class Meta:
        model = Station
        fields = ['id','name','slug','source','infos','latitude','longitude','height','parameters_of_station']
        lookup_field = 'slug'

class ParametersOfStationSerializer(serializers.ModelSerializer):
    # Display Namr rather than id
    parameter = serializers.ReadOnlyField(source='parameter.id')
    class Meta:
        model = ParametersOfStation
        fields = ['parameter']
        lookup_field = 'slug'

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id','name','slug','infos']
        lookup_field = 'slug'
