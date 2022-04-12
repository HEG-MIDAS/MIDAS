from django.shortcuts import render
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import views
from rest_framework.response import Response

from .serializers import StatusSerializer

# Create your views here.
def status(request):
    return True

class StatusView(views.APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = {'status': 'Daijôbu'}
        result = StatusSerializer(data).data
        return Response(result)