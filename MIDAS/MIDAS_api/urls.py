from django.urls import path
from . import views

urlpatterns=[
    path('status/', views.StatusView.as_view(), name='status'),
    path('filter/', views.FilterView.as_view(), name='filter'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('sources/', views.SourceList.as_view(), name='source'),
    path('sources/<str:slug>/', views.SourceDetail.as_view(), name='source_slug'),
    path('stations/', views.StationList.as_view(), name='station'),
    path('stations/<str:slug>/', views.StationDetail.as_view(), name='station_slug'),
    path('parameters/', views.ParameterList.as_view(), name='parameter'),
    path('parameters/<str:slug>/', views.ParameterDetail.as_view(), name='parameter_slug'),
]
