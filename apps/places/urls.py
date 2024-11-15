from django.urls import path
from . import views

app_name = 'places'

urlpatterns = [
    path('festivals/', views.festival_list, name='festival_list'),
    path('travel/', views.travel_destination_list, name='travel_list'),
]
