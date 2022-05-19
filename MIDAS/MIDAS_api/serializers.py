from rest_framework import serializers
from MIDAS_app.models import Source, Station, Parameter, ParametersOfStation, GroupOfFavorite, Favorite

class StatusSerializer(serializers.Serializer):
    """
    It's the status serializer
    """
    status = serializers.CharField(max_length=200)

class StationForSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ['id','name','slug']
        lookup_field = 'slug'
class SourceSerializer(serializers.ModelSerializer):
    # Retrieve Stations by Name (or any value added in slug_field)
    # To retrieve by id, use PrimaryKeyRelatedField
    station = StationForSourceSerializer(many=True)

    class Meta:
        model = Source
        fields = ['id','name','slug','url','infos','station']

# Stations
class ParametersForStationSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='parameter.name')
    slug = serializers.ReadOnlyField(source='parameter.slug')
    infos = serializers.ReadOnlyField(source='parameter.infos')
    class Meta:
        model = ParametersOfStation
        fields = ['name','slug','infos']

class StationSerializer(serializers.ModelSerializer):
    source = serializers.ReadOnlyField(source='source.name')
    parameters_list = ParametersForStationSerializer(many=True,source="parameters_of_station")
    class Meta:
        model = Station
        fields = ['id','name','slug','source','infos','latitude','longitude','height','parameters_list']

# Favorites
class ParametersOfStationFavoriteSerializer(serializers.ModelSerializer):
    parameter = serializers.ReadOnlyField(source='parameter.name')
    station = serializers.ReadOnlyField(source='station.name')
    class Meta:
        model = ParametersOfStation
        fields = ['station','parameter']

class FavoriteSerializer(serializers.ModelSerializer):
    parameters_of_station = ParametersOfStationFavoriteSerializer(many=True)
    class Meta:
        model = Favorite
        fields = ['id','parameters_of_station']

class FavoriteGroupSerializer(serializers.ModelSerializer):
    favorites_list = FavoriteSerializer(many=True,source="favorite")
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = GroupOfFavorite
        fields = ['name','slug','user','favorites_list']

# Views Serializer
class ParametersOfStationSerializer(serializers.ModelSerializer):
    parameter = serializers.ReadOnlyField(source='parameter.id')
    class Meta:
        model = ParametersOfStation
        fields = ['parameter']

# Views Serializer
class ParametersOfStationStationsSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = ['id','name','slug','url','infos']

class ParametersOfStationStationsSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='station.name')
    slug = serializers.ReadOnlyField(source='station.slug')
    infos = serializers.ReadOnlyField(source='station.infos')
    source = ParametersOfStationStationsSourceSerializer(source='station.source')
    latitude = serializers.ReadOnlyField(source='station.latitude')
    longitude = serializers.ReadOnlyField(source='station.longitude')
    height = serializers.ReadOnlyField(source='station.height')
    class Meta:
        model = ParametersOfStation
        fields = ['name','slug','infos','source','latitude','longitude','height']

class ParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parameter
        fields = ['id','name','slug','infos']
