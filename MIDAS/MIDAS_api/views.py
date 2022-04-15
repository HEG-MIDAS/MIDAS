from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework import views
from rest_framework.response import Response
from rest_framework import generics
from .serializers import StatusSerializer, SourceSerializer, StationSerializer, ParameterSerializer, ParametersOfStationSerializer
from MIDAS_app.models import Source, Station, Parameter, ParametersOfStation

# Create your views here.
def status(request):
    return True

class LocalPerm(BasePermission):
    def has_permission(self, request, view):
        print(request.META['REMOTE_ADDR'])
        if(request.META['REMOTE_ADDR'] == '127.0.0.1'):
            return True

        return False

class StatusView(views.APIView):
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

    def get(self, request):
        data = {'status': 'Daijôbu'}
        result = StatusSerializer(data).data
        return Response(result)

class SearchView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

    def post(self, request):
        """
            Search data in files
        """
        if('sources' not in request.data or 'stations' not in request.data or 'parameters' not in request.data):
            return Response({"error":"Missing POST body"}, status=400)

        sources = request.data["sources"]
        stations = request.data["stations"]
        parameters = request.data["parameters"]
        if(type(sources) is list):
            for source in sources:
                if(type(stations) is list):
                    for station in stations:
                        print(station)

        return Response({"error":"temporary unavailable"}, status=400)




class FilterView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

    def post(self, request):
        """
            Filter data. If stations, filter params, if sources, filter stations
        """
        data = []
        if('stations' in request.data):
            stations = request.data['stations']
            if(type(stations) is list):
                station = list(Station.objects.filter(slug__in=stations).values_list('id', flat=True))
            elif(type(stations) is str):
                station = list(Station.objects.filter(slug=stations).values_list('id', flat=True))
            query = ParametersOfStation.objects.filter(station__in=station)
            serializer = ParametersOfStationSerializer(query,many=True)
            for ser in serializer.data:
                if(ser['parameter'] not in data):
                    data.append(ser['parameter'])
            query = Parameter.objects.filter(id__in=data)
            serializer = ParameterSerializer(query,many=True)
            data = serializer.data
        elif('sources' in request.data):
            sources = request.data['sources']
            if(type(sources) is list):
                source = list(Source.objects.filter(slug__in=sources).values_list('id', flat=True))
            elif(type(sources) is str):
                source = list(Source.objects.filter(slug=sources).values_list('id', flat=True))
            query = Station.objects.filter(source__in=source)
            serializer = StationSerializer(query,many=True)
            data = serializer.data
        else:
            return Response({"error":"No POST body found"}, status=400)

        if(len(data)>0):
            return Response(data)
        else:
            return Response({"error":"No content found"}, status=400)

class SourceList(generics.ListAPIView):
    """
        List all Sources
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

class SourceDetail(generics.RetrieveAPIView):
    """
        Retrieve a specific Source by the slug

        To make it work with both the pk and the slug,
        In urls.py:
        path('sources/<int:pk>/', views.SourceDetail.as_view(), name='source_slug'),
        path('sources/<str:slug>/', views.SourceDetail.as_view(), name='source_slug',lookup_field='slug'),

        Remove the lookup_field frm this view ! (Needs to do it for all *Detail views)
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]
    lookup_field = 'slug'

class StationList(generics.ListAPIView):
    """
        List all Stations
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

class StationDetail(generics.RetrieveAPIView):
    """
        Retrieve a specific Station by the slug
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]
    lookup_field = 'slug'

class ParameterList(generics.ListAPIView):
    """
        List all Parameters
    """
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

class ParameterDetail(generics.RetrieveAPIView):
    """
        Retrieve a specific Parameter by the slug
    """
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]
    lookup_field = 'slug'
