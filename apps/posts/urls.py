from django.urls import path
from .views import main, post_list, post_create, post_update, post_delete

app_name = 'posts'

urlpatterns = [
    path('', main, name='main'),
    path('posts/', post_list, name='post_list'),
    path('posts/create/', post_create, name='post_create'),
    path('posts/<int:pk>/update/', post_update, name='post_update'),
    path('posts/<int:pk>/delete/', post_delete, name='post_delete'),
]
