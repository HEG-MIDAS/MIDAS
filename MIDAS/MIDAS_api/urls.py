from django.urls import path
from . import views

urlpatterns=[
    path('status/', views.StatusView.as_view(), name='status'),
]
