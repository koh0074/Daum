from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.main, name="user"),
    path("signup/", views.signup, name="signup"),
    path("login/", views.login, name="login"),
    path("logout/", views.logout, name="logout"),
    # 친구 기능 관련 URL
    path('search/', views.search_user, name='search_user'),
    path('send_request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('requests/', views.friend_requests, name='friend_requests'),
    path('friends/', views.friends_list, name='friends_list'),
    path('accept_request/<int:request_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('decline_request/<int:request_id>/', views.decline_friend_request, name='decline_friend_request'),
    path('get_friend_requests/', views.get_friend_requests, name='get_friend_requests'),  # 이 부분 추가
]