from django.urls import path
from . import views

urlpatterns = [
    path('route/', views.OptimizeRouteView.as_view(), name='optimize-route'),
    path('route/map/', views.map_view, name='map'),
]
