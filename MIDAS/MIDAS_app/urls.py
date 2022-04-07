from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView

urlpatterns=[
    path('', views.index, name='index'),
    path('manage-data/', views.manage_data, name='manage_data'),
    path('harvest-data/', views.harvest_data, name='harvest_data'),
    path('statut/', views.statut, name='statut'),
    path('statut/<slug:source>.svg', views.statut_badge, name='statut_badge'),
    path('change-password/', PasswordChangeView.as_view(template_name='registration/change_password.html'), name='password_change'),
    path('change-password-success/', PasswordChangeDoneView.as_view(template_name='registration/change_password_success.html'), name='password_change_done'),
]
