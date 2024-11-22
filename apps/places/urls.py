from django.urls import path
from . import views
from django.conf import settings  # settings 가져오
from django.conf.urls.static import static

app_name = 'places'

urlpatterns = [
    path('festivals/', views.festival_list, name='festival_list'),
    path('travel/', views.travel_destination_list, name='travel_list'),
    path('bookmark/<int:festival_id>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('travel/bookmark/<int:destination_id>/', views.toggle_destination_bookmark, name='toggle_destination_bookmark'),
    path('bookmarked_festivals/', views.bookmarked_festivals, name='bookmarked_festivals'),
    path('search/', views.search_results, name='search_results'),
    path('load_tab/<str:tab_name>/', views.load_tab, name='load_tab'),
]
if settings.DEBUG:  # 개발 환경에서만 동작
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
