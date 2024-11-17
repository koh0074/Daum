from django.urls import path
from .views import main, post_list, post_create, post_update, post_delete
from . import views

app_name = 'posts'

urlpatterns = [
    path('', main, name='main'),
    path('posts/', post_list, name='post_list'),
    path('posts/create/', post_create, name='post_create'),
    path('posts/<int:pk>/update/', post_update, name='post_update'),
    path('posts/<int:pk>/delete/', post_delete, name='post_delete'),

    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/like/', views.toggle_like, name='toggle_like'),
    path('post/<int:post_id>/bookmark/', views.toggle_bookmark, name='toggle_bookmark'),

    path('friends/', views.friends_posts, name='friends_posts'),
]
