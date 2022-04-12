from django.shortcuts import render
from rest_framework import views
from rest_framework.response import Response

from .serializers import StatusSerializer

# Create your views here.
def status(request):
    return True

class StatusView(views.APIView):

    def get(self, request):
        data = [{'status': 'Daijôbu'}]
        result = StatusSerializer(data).data
        return Response(result)