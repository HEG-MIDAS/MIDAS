from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns=[
    path('status/', views.StatusView.as_view(), name='status'),
    path('status/third-party/', views.StatusThirdPartyView.as_view(), name='status_third_party'),
    path('filter/', views.FilterView.as_view(), name='filter'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('sources/', views.SourceList.as_view(), name='source'),
    path('sources/<int:pk>/', views.SourceDetail.as_view(), name='source_pk'),
    path('sources/<str:slug>/', views.SourceDetail.as_view(lookup_field='slug'), name='source_slug'),
    path('stations/', views.StationList.as_view(), name='station'),
    path('stations/<int:pk>/', views.StationDetail.as_view(), name='station_pk'),
    path('stations/<str:slug>/', views.StationDetail.as_view(lookup_field='slug'), name='station_slug'),
    path('parameters/', views.ParameterList.as_view(), name='parameter'),
    path('parameters/<int:pk>/', views.ParameterDetail.as_view(), name='parameter_pk'),
    path('parameters/<str:slug>/', views.ParameterDetail.as_view(lookup_field='slug'), name='parameter_slug'),
    path('favorites-group/', views.FavoriteGroupList.as_view(), name='favorite'),
    path('favorites-group/<int:pk>/', views.FavoriteGroupDetail.as_view(), name='favorite_pk'),
    path('favorites-group/<str:slug>/', views.FavoriteGroupDetail.as_view(lookup_field='slug'), name='favorite_slug'),
    path('doc/', TemplateView.as_view(template_name='apidoc.html'), name='doc'),
]
