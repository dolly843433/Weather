from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('settings/', views.settings_view, name='settings_view'),
    path('update_weather/', views.update_weather, name='update_weather'),
]
