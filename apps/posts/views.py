from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Like, Bookmark
from apps.accounts.models import FriendRequest
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import date

def main(request):
    """메인 페이지"""
    return render(request, 'main.html')

def get_friends(user):
    """현재 사용자의 친구 목록을 가져오는 함수"""
    accepted_requests = FriendRequest.objects.filter(from_user=user, is_accepted=True)
    accepted_requests |= FriendRequest.objects.filter(to_user=user, is_accepted=True)
    
    # 친구 목록을 추출
    friends = set()
    for request in accepted_requests:
        if request.from_user == user:
            friends.add(request.to_user)
        else:
            friends.add(request.from_user)
    return friends

from django.db.models import Q

@login_required
def post_list(request):
    """일반 게시글 목록: 친구가 아닌 사용자의 게시글만 표시하고, 본인이 작성한 게시글은 제외"""
    sort = request.GET.get('sort', 'latest')

    # 친구 목록 가져오기
    friends = get_friends(request.user)
    
    # 디버깅용 출력
    print(f"Friends: {[friend.username for friend in friends]}")

    # 친구와 본인을 제외한 게시글 가져오기
    if friends:
        posts = Post.objects.exclude(Q(author__in=friends) | Q(author=request.user))
    else:
        posts = Post.objects.exclude(author=request.user)

    # 디버깅용 출력
    print(f"Post count before sorting: {posts.count()}")

    # 사용자가 찜한 게시글 목록 가져오기
    user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True)

    # 정렬 옵션 처리
    if sort == 'latest':
        posts = posts.order_by('-created_at')
    elif sort == 'rating':
        posts = posts.order_by('-rating')
    elif sort == 'likes':
        posts = sorted(posts, key=lambda p: p.like_set.count(), reverse=True)

    # 디버깅용 출력
    print(f"Post count after sorting: {len(posts) if isinstance(posts, list) else posts.count()}")

    return render(request, 'posts/posts_list.html', {
        'posts': posts,
        'user_bookmarks': user_bookmarks,
        'sort': sort
    })

@login_required
def friends_posts(request):
    """친구의 게시글만 표시"""
    friends = get_friends(request.user)
    posts = Post.objects.filter(author__in=friends)

    # 사용자가 찜한 게시글 목록 가져오기
    user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('post_id', flat=True)

    return render(request, 'posts/friends_posts.html', {
        'posts': posts,
        'user_bookmarks': user_bookmarks,
        'title': "친구의 여행일기"
    })

@login_required
def post_create(request):
    """게시글 생성"""
    tags_list = ["맛집탐방", "나들이", "지역축제", "이색체험", "캠핑"]

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_list')
        else:
            print("폼 에러:", form.errors)
    else:
        # 폼 생성 시 기본 별점 값 설정
        form = PostForm(initial={'rating': 0})

    return render(request, 'posts/posts_create.html', {'form': form, 'tags': tags_list})


@login_required
def post_update(request, pk):
    """게시글 수정"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # 이미지가 수정된 경우 content에 <img> 태그 추가
            if request.FILES.get('image'):
                image = request.FILES['image']
                post.content += f'\n<img src="{post.image.url}" alt="{post.title}" style="max-width:100%; height:auto;">'
            
            post.save()
            form.save_m2m()  # ManyToManyField 저장
            return redirect('posts:post_list')
    else:
        form = PostForm(instance=post)
    
    return render(request, 'posts/posts_update.html', {'form': form, 'post': post})

@login_required
def post_delete(request, pk):
    """게시글 삭제"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        return redirect('posts:post_list')
    
    return render(request, 'posts/posts_delete.html', {'post': post})

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all()
    is_liked = False
    is_bookmarked = False
    if request.user.is_authenticated:
        is_liked = Like.objects.filter(user=request.user, post=post).exists()
        is_bookmarked = Bookmark.objects.filter(user=request.user, post=post).exists()

    context = {
        'post': post,
        'comments': comments,
        'is_liked': is_liked,
        'is_bookmarked': is_bookmarked,
    }
    return render(request, 'posts/post_detail.html', context)

@login_required
@require_POST
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    content = request.POST.get('content')
    if content:
        Comment.objects.create(post=post, author=request.user, content=content)
    return redirect('posts:post_detail', post_id=post_id)

@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()
        is_liked = False
    else:
        is_liked = True
    return JsonResponse({'is_liked': is_liked})

@login_required
@require_POST
def toggle_bookmark(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
        is_bookmarked = False
    else:
        is_bookmarked = True
    return JsonResponse({'is_bookmarked': is_bookmarked})