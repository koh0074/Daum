from django.shortcuts import render, get_object_or_404
from .models import Festival, TravelDestination, FestivalBookmark, TravelBookmark
from datetime import date
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

def festival_list(request):
    # 모든 축제 정보를 가져옵니다.
    festivals = Festival.objects.all()
    festival_count = festivals.count()

    # 현재 사용자가 찜한 축제 목록 가져오기 (로그인한 경우만)
    user_bookmarks = []
    if request.user.is_authenticated:
        user_bookmarks = FestivalBookmark.objects.filter(user=request.user).values_list('festival_id', flat=True)

    # 남은 일수를 계산하고 찜 여부를 추가
    for festival in festivals:
        days_left = (festival.start_date - date.today()).days
        festival.days_left = f"D-{days_left}" if days_left >= 0 else "종료됨"
        festival.is_bookmarked = festival.id in user_bookmarks

    context = {
        'festivals': festivals,
        'festival_count': festival_count,
    }
    return render(request, 'places/festival_list.html', context)

def travel_destination_list(request):
    destinations = TravelDestination.objects.all()
    destination_count = destinations.count()
    return render(request, 'places/travel_list.html', {
        'destinations': destinations,
        'destination_count': destination_count
    })

@login_required
@require_POST
def toggle_bookmark(request, festival_id):
    festival = get_object_or_404(Festival, id=festival_id)
    bookmark, created = FestivalBookmark.objects.get_or_create(user=request.user, festival=festival)
    
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True

    return JsonResponse({'is_bookmarked': is_bookmarked})

@login_required
@require_POST
def toggle_destination_bookmark(request, destination_id):
    destination = get_object_or_404(TravelDestination, id=destination_id)
    bookmark, created = TravelBookmark.objects.get_or_create(user=request.user, destination=destination)
    
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True

    return JsonResponse({'is_bookmarked': is_bookmarked})

@login_required
def bookmarked_festivals(request):
    """사용자가 찜한 축제만 표시"""
    bookmarks = FestivalBookmark.objects.filter(user=request.user)
    festivals = [bookmark.festival for bookmark in bookmarks]

    # 남은 일수 계산
    upcoming_festivals = []
    for festival in festivals:
        days_left = (festival.start_date - date.today()).days
        festival.days_left = f"D-{days_left}" if days_left >= 0 else "종료됨"
        
        # 디데이가 7일 이하인 경우와 그 외로 분리
        if days_left <= 7 and days_left >= 0:
            upcoming_festivals.append(festival)
    
    context = {
        'upcoming_festivals': upcoming_festivals,
        'all_festivals': festivals,  # 모든 축제 목록을 추가
        'title': "내가 찜한 축제"
    }
    return render(request, 'places/bookmarked_festivals.html', context)

from django.shortcuts import render, get_object_or_404
from .models import Festival, TravelDestination, FestivalBookmark, TravelBookmark
from apps.posts.models import Post
from apps.accounts.models import FriendRequest
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from datetime import date
from django.contrib.auth.models import AnonymousUser

def get_friends(user):
    """현재 사용자의 친구 목록을 가져오는 함수"""
    if isinstance(user, AnonymousUser):
        return []
    accepted_requests = FriendRequest.objects.filter(from_user=user, is_accepted=True) | \
                        FriendRequest.objects.filter(to_user=user, is_accepted=True)
    friends = set()
    for request in accepted_requests:
        if request.from_user == user:
            friends.add(request.to_user)
        else:
            friends.add(request.from_user)
    return friends

def search_results(request):
    query = request.GET.get('q', '')
    friends = get_friends(request.user) if request.user.is_authenticated else []

    # 검색어가 포함된 축제, 여행지, 게시글을 검색합니다.
    festivals = Festival.objects.filter(name__icontains=query) | Festival.objects.filter(description__icontains=query)
    destinations = TravelDestination.objects.filter(name__icontains=query) | TravelDestination.objects.filter(description__icontains=query)
    
    if request.user.is_authenticated:
        others_posts = Post.objects.filter(content__icontains=query).exclude(author__in=friends).exclude(author=request.user)
        friends_posts = Post.objects.filter(content__icontains=query, author__in=friends)
    else:
        others_posts = Post.objects.filter(content__icontains=query)
        friends_posts = []

    context = {
        'query': query,
        'festivals': festivals,
        'destinations': destinations,
        'others_posts': others_posts,
        'friends_posts': friends_posts,
        'title': "검색 결과"
    }
    return render(request, 'places/search_results.html', context)

def load_tab(request, tab_name):
    """AJAX를 통해 탭 콘텐츠를 동적으로 로드"""
    if tab_name == 'festivals':
        festivals = Festival.objects.all()
        return render(request, 'places/partials/festivals_tab.html', {'festivals': festivals})

    elif tab_name == 'travel_destinations':
        destinations = TravelDestination.objects.all()
        return render(request, 'places/partials/travel_destinations_tab.html', {'destinations': destinations})

    elif tab_name == 'others_posts':
        if request.user.is_authenticated:
            posts = Post.objects.exclude(author=request.user)
        else:
            posts = Post.objects.all()
        return render(request, 'places/partials/others_posts_tab.html', {'posts': posts})

    elif tab_name == 'friends_posts':
        if request.user.is_authenticated:
            friends_posts = Post.objects.filter(author__in=get_friends(request.user))
        else:
            friends_posts = []
        return render(request, 'places/partials/friends_posts_tab.html', {'posts': friends_posts})

    return render(request, 'places/partials/not_found.html')
