from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comment, Like, Bookmark
from apps.accounts.models import FriendRequest
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from datetime import date
import json
from django.views.decorators.csrf import csrf_exempt

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
        posts = Post.objects.filter(is_draft=False).exclude(Q(author__in=friends) | Q(author=request.user))
    else:
        posts = Post.objects.filter(is_draft=False).exclude(author=request.user)

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
    posts = Post.objects.filter(author__in=friends, is_draft=False)

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

    # 현재 사용자 임시 저장 게시글 수 계산
    draft_count = Post.objects.filter(author=request.user, is_draft=True).count()
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            if 'save_draft' in request.POST:
                post.is_draft = True
            return redirect('posts:post_list')
        else:
            print("폼 에러:", form.errors)
    else:
        # 폼 생성 시 기본 별점 값 설정
        form = PostForm(initial={'rating': 0})

    return render(request, 'posts/posts_create.html', {
        'form': form,
        'tags': tags_list,
        'draft_count': draft_count,  # 임시 저장 게시글 수 전달
    })


@login_required
def post_update(request, pk):
    """게시글 수정"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        # POST 데이터에서 tags 값을 전처리
        tags = request.POST.getlist('tags', [])
        # 빈 태그 제거
        valid_tags = [tag.strip() for tag in tags if tag.strip()]
        request.POST = request.POST.copy()
        request.POST.setlist('tags', valid_tags)

        form = PostForm(request.POST, request.FILES, instance=post)
        
        if form.is_valid():
            # content 필드가 비어 있는지 확인
            if not form.cleaned_data.get('content', '').strip():
                form.add_error('content', '내용을 입력해주세요.')
                return render(request, 'posts/posts_update.html', {'form': form, 'post': post})
            
            post = form.save(commit=False)
            
            # 이미지가 수정된 경우 content에 <img> 태그 추가
            if request.FILES.get('image'):
                image = request.FILES['image']
                post.content += f'\n<img src="{post.image.url}" alt="{post.title}" style="max-width:100%; height:auto;">'
            
            post.save()
            form.save_m2m()  # ManyToManyField 저장
            return redirect('profiles:profile_main')  # 수정 후 profile_main.html로 이동
        else:
            # 폼 검증 실패 시 디버깅 출력
            print("폼 에러:", form.errors)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'posts/posts_update.html', {'form': form, 'post': post})


@login_required
def post_delete(request, pk):
    """게시글 삭제"""
    post = get_object_or_404(Post, pk=pk)
    
    if request.method == 'POST':
        post.delete()
        return redirect('profiles:profile_main')
    
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
        'is_bookmarked': is_bookmarked,  # 북마크 상태 전달
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
    try:
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            is_liked = False
        else:
            is_liked = True

        return JsonResponse({'success': True, 'is_liked': is_liked})
    except Exception as e:
        print("Error in toggle_like:", str(e))
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def toggle_bookmark(request, post_id):
    try:
        post = get_object_or_404(Post, id=post_id)
        bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

        if not created:
            bookmark.delete()
            is_bookmarked = False
        else:
            is_bookmarked = True

        return JsonResponse({'success': True, 'is_bookmarked': is_bookmarked})
    except Exception as e:
        print("Error in toggle_bookmark:", str(e))
        return JsonResponse({'success': False, 'error': str(e)}, status=400)



@csrf_exempt
@login_required
def save_draft(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()

            if not title or not content:
                return JsonResponse({'error': '제목과 내용을 모두 입력해야 합니다.'}, status=400)

            post, created = Post.objects.update_or_create(
                title=title,
                author=request.user,
                defaults={
                    'content': content,
                    'is_draft': True,
                }
            )

            # 임시 저장된 게시글 수 계산
            draft_count = Post.objects.filter(author=request.user, is_draft=True).count()

            return JsonResponse({'message': 'Draft saved successfully', 'post_id': post.id, 'draft_count': draft_count})
        except Exception as e:
            print("Error:", e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)
