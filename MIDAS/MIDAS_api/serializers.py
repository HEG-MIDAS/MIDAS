from rest_framework import serializers
from MIDAS_app.models import Source, Station, Parameter, ParamatersOfStation

class StatusSerializer(serializers.Serializer):
    """
    It's the status serializer
    """
    status = serializers.CharField(max_length=200)

class SourceSerializer(serializers.ModelSerializer):
    # Retrieve Stations by Name (or any value added in slug_field)
    # To retrieve by id, use PrimaryKeyRelated
    station = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Source.objects.all())

    class Meta:
        model = Source
        fields = ['name','slug','url','infos','station']
        lookup_field = 'slug'

class StationSerializer(serializers.ModelSerializer):
    # Display Namr rather than id
    source = serializers.ReadOnlyField(source='source.name')
    paramaters_of_station = serializers.SlugRelatedField(many=True, slug_field='name', queryset=ParamatersOfStation.objects.all())
    class Meta:
        model = Station
        fields = ['name','slug','source','infos','latitude','longitude','height','paramaters_of_station']
        lookup_field = 'slug'

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['name','slug','infos']
        lookup_field = 'slug'
