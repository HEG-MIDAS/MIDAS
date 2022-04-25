import numpy as np
import datetime
from os import listdir
from os.path import isdir,join
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS
from rest_framework import views
from rest_framework.response import Response
from rest_framework import generics
from django.conf import settings
from .serializers import StatusSerializer, SourceSerializer, StationSerializer, ParameterSerializer, ParametersOfStationSerializer, FavoriteGroupSerializer
from MIDAS_app.models import Source, Station, Parameter, ParametersOfStation, GroupOfFavorite
import requests

# Create your views here.
def status(request):
    return True

class LocalPerm(BasePermission):
    def has_permission(self, request, view):
        if(request.META['REMOTE_ADDR'] == '127.0.0.1'):
            return True

        return False


class StatusView(views.APIView):
    """
    Return the status of the website, more precisely, if the sources of the website are all available, some, or none of them.

    Returns
    -------
    json -> Response
    """
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

    def get(self, request):
        data = {}
        dic = {'sabra':'https://www.ropag-data.ch/gechairmo/i_extr.php','climacity':'http://www.climacity.org/Axis/'}
        count = 0
        for k in dic:
            try:
                resp = requests.get(dic[k])
                if resp.status_code != 200:
                    count+=1
            except:
                count+=1
        if(count == 0):
            data['status'] = "Toutes les sources sont opérationnelles"
        elif(count != 0 and count < len(dic)):
            data['status'] = "Certaines sources ne sont pas accessibles"
        else:
            data['status'] = "Aucune des sources n\'est accessible"

        result = StatusSerializer(data).data
        return Response(result)


class SearchView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

    def post(self, request):
        """Search datas in files

        POST Parameters
        ----------
        sources : array
            list of sources (required)
        stations : array
            list of stations (required)
        parameters : array
            list of parameters (required)
        start_date: date
            Date of to begin retrieving (included)
            If specified alongside end_date, limit is overriden
            If specified alone, override order to ASC
        end_date: date
            Date of to stop retrieving (included)
            If specified alongside start_date, limit is overriden
            If specified alone, override order to DESC
        limit: int
            number of value to display. (default 20, max 100)
        order: str
            order in which the file is read (default ASC, choice [ASC, DESC])

        Returns
        -------
        json
            list of values for the corresponding parameters in json format
        """
        if('sources' not in request.data or 'stations' not in request.data or 'parameters' not in request.data):
            return Response({"error":"Missing POST body"}, status=400)

        results = {}
        # Get the folder for transformed files
        transformedFolder = join(settings.MEDIA_ROOT,'transformed')
        # Get all the sources we have
        allSources = listdir(transformedFolder)
        # Get required params
        sources = request.data["sources"]
        stations = request.data["stations"]
        parameters = request.data["parameters"]
        # Set default (Might be better to move to settings?)
        limitDefault = 20
        orderDefault = 'ASC'
        # Setting the optional values
        limitMax = request.data["limit"] if ('limit' in request.data) else limitDefault
        limitMax = limitMax if (type(limitMax) is int) else limitDefault
        limitMax = limitMax if limitMax > 0 else 1
        limitMax = limitMax if limitMax <= 100 else 100
        order = request.data["order"] if ('order' in request.data) else orderDefault
        order = order if (order in ['ASC','DESC']) else orderDefault
        # Date
        try:
            start_date = datetime.datetime.strptime(request.data["start_date"],"%Y-%m-%d %H:%M:%S") if ('start_date' in request.data) else None
            end_date = datetime.datetime.strptime(request.data["end_date"],"%Y-%m-%d %H:%M:%S") if ('end_date' in request.data) else None
            if(start_date != None and end_date != None):
                # Don't use the limit if both start and end date exists
                limitMax = None
                if(end_date-start_date < datetime.timedelta(days=0)):
                    return Response({"error":"End Date smaller than start Date"}, status=400)
            # If only end date is giving, get <limit> from the end of the file
            elif(start_date == None and end_date != None):
                order = 'DESC'
            # If only start date is giving, get <limit> from the beginning of the file
            elif(start_date != None and end_date == None):
                order = 'ASC'
        except:
            return Response({"error":"Incorrect Date"}, status=400)
        # Get a list of all parameters
        parameterQuery = Parameter.objects.filter(slug__in=parameters)
        parameterSerializer = ParameterSerializer(parameterQuery,many=True)
        parameterData = parameterSerializer.data
        parametersList = []
        for param in parameterData:
            parametersList.append(param["id"])
        # Check if sources is a list (Do we check if it's a single string?)
        if(type(sources) is list):
            for source in sources:
                # General try, catch, might be worth separating?
                try:
                    # Get the source and station corresponding to the parameters
                    sourceQuery = Source.objects.get(slug=source)
                    sourceSerializer = SourceSerializer(sourceQuery)
                    sourceData = sourceSerializer.data
                    stationQuery = Station.objects.filter(slug__in=stations).filter(source=sourceQuery)
                    stationSerializer = StationSerializer(stationQuery,many=True)
                    stationData = stationSerializer.data
                    if(len(stationData) < 1 or len(sourceData) < 1):
                        raise Exception
                    # Check if source in db has a folder
                    if(sourceData["name"] in allSources):
                        results[sourceData["name"]] = {}
                        sourceFolder = join(transformedFolder,sourceData["name"])
                        for station in stationData:
                            # Filter the station file
                            matchingStation = [s for s in listdir(sourceFolder) if station["name"] in s]
                            if(len(matchingStation) > 0):
                                stationFolder = join(sourceFolder,matchingStation[0])
                                results[sourceData["name"]][station["name"]] = {}
                                # Retrieve list of params for the station
                                stationParam = Station.objects.get(slug=station["slug"])
                                paramStationQuery = ParametersOfStation.objects.filter(station=stationParam).filter(parameter__in=parametersList)
                                paramStationSerializer = ParametersOfStationSerializer(paramStationQuery,many=True)
                                paramStationData = paramStationSerializer.data
                                # Create a list of the parameters we need
                                paramList = []
                                for param in paramStationData:
                                    p = list(filter(lambda p: p["id"] == param["parameter"],parameterData))
                                    paramList.append(p[0]["name"])
                                # FILE MANIPULATION
                                file = open(stationFolder)
                                # Filter Header to retrieve the index when we split
                                header = file.readline().strip().split(",")
                                headerIndex = []
                                for i in range(1,len(header)):
                                    p = header[i].strip('*')
                                    if(p in paramList):
                                        headerIndex.append(i)
                                limit = 0
                                lines = file.readlines()
                                # Reverse the file
                                if(order == 'DESC'):
                                    lines = reversed(lines)
                                for line in lines:
                                    l = line.strip().split(",")
                                    # If the start and end date exist and the line date isn't between them
                                    if(start_date != None and end_date != None and not start_date <= datetime.datetime.strptime(l[0],"%Y-%m-%d %H:%M:%S") <= end_date):
                                        continue
                                    results[sourceData["name"]][station["name"]][l[0]] = {}
                                    for index in headerIndex:
                                        results[sourceData["name"]][station["name"]][l[0]][header[index]] = np.double(l[index]) if(l[index] != "" and l[index] != " ") else l[index]
                                    limit += 1
                                    if(limitMax != None and limit == limitMax):
                                        break
                                file.close()
                            else:
                                raise Exception
                except:
                    return Response({"error":"An error occured"}, status=500)

        if(len(results)>0):
            return Response(results, status=200)
        return Response({"error":"No Data found"}, status=400)


class FilterView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]

    def post(self, request):
        """Filter data. If stations, filter params, if sources, filter stations

        POST Parameters
        ----------
        sources : array or string
            list of sources or one source (required)
        stations : array or string
            list of stations or one station

        Returns
        -------
        json
            list of stations or parameters for the corresponding parameters in json format
            source -> station -> timestamp -> parameters
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
    """List all Sources
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]


class SourceDetail(generics.RetrieveAPIView):
    """Retrieve a specific Source by the slug

    To make it work with both the pk and the slug,
    In urls.py:
    path('sources/<int:pk>/', views.SourceDetail.as_view(), name='source_pk'),
    path('sources/<str:slug>/', views.SourceDetail.as_view(), name='source_slug',lookup_field='slug'),

    Remove the lookup_field from this view ! (Needs to do it for all *Detail views)
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]
    lookup_field = 'slug'


class StationList(generics.ListAPIView):
    """List all Stations
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]


class StationDetail(generics.RetrieveAPIView):
    """Retrieve a specific Station by the slug
    """
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]
    lookup_field = 'slug'


class ParameterList(generics.ListAPIView):
    """List all Parameters
    """
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]


class ParameterDetail(generics.RetrieveAPIView):
    """Retrieve a specific Parameter by the slug
    """
    queryset = Parameter.objects.all()
    serializer_class = ParameterSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated|LocalPerm]
    lookup_field = 'slug'


class FavoriteGroupList(generics.ListAPIView):
    """List all Parameters
    """
    queryset = GroupOfFavorite.objects.all()
    serializer_class = FavoriteGroupSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]


class FavoriteGroupDetail(generics.RetrieveAPIView):
    """Retrieve a specific Parameter by the slug
    """
    queryset = GroupOfFavorite.objects.all()
    serializer_class = FavoriteGroupSerializer
    authentication_classes = [SessionAuthentication,BasicAuthentication]
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'
