from django.urls import path
from . import views

urlpatterns=[
    path('', views.index, name='index'),
    path('manage-data/', views.manage_data, name='manage_data'),
]
