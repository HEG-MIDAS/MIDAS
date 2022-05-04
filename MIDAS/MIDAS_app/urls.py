from django.urls import path
from . import views
from django.contrib.auth.views import PasswordChangeDoneView, PasswordChangeView,PasswordResetDoneView, PasswordResetView, PasswordResetCompleteView

urlpatterns=[
    path('', views.index, name='index'),
    path('manage-data/', views.manage_data, name='manage_data'),
    path('harvest-data/', views.harvest_data, name='harvest_data'),
    path('statut/', views.statut, name='statut'),
    path('test/', views.test, name='test'),
    path('account/favorites', views.favorite_profile, name='account_favorites'),
    path('account/favorites/delete/<str:slug>', views.favorite_deletion, name='account_favorite_deletion'),
    path('account/add-token/', views.manage_token, name='account_token'),
    path('statut/<slug:source>.svg', views.statut_badge, name='statut_badge'),
    path('change-password/', PasswordChangeView.as_view(template_name='registration/password_change_form.html'), name='password_change'),
    path('change-password-success/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('reset-password/', PasswordResetView.as_view(template_name='registration/password_reset_form.html'), name='password_reset'),
    path('reset-password-success/', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset-success/', PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
]
