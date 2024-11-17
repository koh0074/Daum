from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from apps.posts.models import Post, Bookmark
from apps.profiles.models import Profile
from apps.places.models import Festival, TravelDestination, FestivalBookmark, TravelBookmark
from apps.accounts.models import FriendRequest
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q

User = get_user_model()  # 변경: 기본 User 모델 대신 커스텀 User 모델을 가져옴

@login_required
def profile(request):
    """사용자 프로필 페이지"""
    user = request.user
    # 사용자가 작성한 게시글 가져오기
    posts = Post.objects.filter(author=user).order_by('-created_at')
    
    # 친구 목록 가져오기 (양방향 친구 관계 확인)
    friends_ids_from = FriendRequest.objects.filter(from_user=user, is_accepted=True).values_list('to_user', flat=True)
    friends_ids_to = FriendRequest.objects.filter(to_user=user, is_accepted=True).values_list('from_user', flat=True)
    friends_ids = set(friends_ids_from).union(set(friends_ids_to))
    friends = User.objects.filter(id__in=friends_ids)

    # 사용자가 찜한 축제와 여행지 가져오기
    festival_bookmarks = FestivalBookmark.objects.filter(user=user)
    travel_bookmarks = TravelBookmark.objects.filter(user=user)
    post_bookmarks = Bookmark.objects.filter(user=user)

    return render(request, 'profiles/profile_main.html', {
        'user': user,
        'posts': posts,
        'friends': friends,
        'friends_count': len(friends),
        'nickname': user.first_name if user.first_name else user.username,
        'festival_bookmarks': festival_bookmarks,
        'travel_bookmarks': travel_bookmarks,
        'post_bookmarks': post_bookmarks,
    })


@login_required
def edit_nickname(request):
    if request.method == 'POST':
        new_nickname = request.POST.get('nickname')
        if new_nickname:
            request.user.first_name = new_nickname
            request.user.save()
        return redirect('profiles:profile_main')

    return render(request, 'profiles/profile_main.html')

@login_required
def edit_profile_image(request):
    if request.method == 'POST':
        profile_image = request.FILES.get('profile_image')
        profile, created = Profile.objects.get_or_create(user=request.user)
        if profile_image:
            profile.image = profile_image
            profile.save()
        return redirect('profiles:profile_main')

    return render(request, 'profiles/profile_main.html')


@login_required
def logout(request):
    """로그아웃"""
    auth_logout(request)
    return redirect('accounts:login')

@login_required
def friend_profile(request, username):
    """특정 사용자의 프로필 페이지"""
    friend = get_object_or_404(User, username=username)
    posts = Post.objects.filter(author=friend)

    # 현재 로그인한 사용자가 이 친구와 친구인지 확인
    is_friend = FriendRequest.objects.filter(
        Q(from_user=request.user, to_user=friend, is_accepted=True) |
        Q(from_user=friend, to_user=request.user, is_accepted=True)
    ).exists()

    # 해당 사용자의 친구 목록 조회 (자기 자신을 제외)
    friends = FriendRequest.objects.filter(
        Q(from_user=friend, is_accepted=True) | Q(to_user=friend, is_accepted=True)
    )
    friends_list = User.objects.filter(
        Q(id__in=friends.values_list('from_user', flat=True)) |
        Q(id__in=friends.values_list('to_user', flat=True))
    ).exclude(id=friend.id)  # 자기 자신을 제외
    friends_count = friends_list.count()

    return render(request, 'profiles/friend_profile.html', {
        'friend': friend,
        'posts': posts,
        'is_friend': is_friend,
        'friends_count': friends_count,
        'friends_list': friends_list
    })

@login_required
def delete_friend(request, username):
    """친구 삭제"""
    friend = get_object_or_404(User, username=username)
    FriendRequest.objects.filter(from_user=request.user, to_user=friend, is_accepted=True).delete()
    FriendRequest.objects.filter(from_user=friend, to_user=request.user, is_accepted=True).delete()
    return JsonResponse({'status': 'deleted'})

@login_required
def send_friend_request(request, username):
    """친구 요청"""
    to_user = get_object_or_404(User, username=username)
    if not FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return JsonResponse({'status': 'requested'})
