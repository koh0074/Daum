from django.shortcuts import render, get_object_or_404, redirect
from .models import Post
from .forms import PostForm
from django.contrib.auth.decorators import login_required

def main(request):
    """메인 페이지"""
    return render(request, 'main.html')

def post_list(request):
    # GET 요청에서 'sort' 파라미터를 가져옵니다 (기본값은 'latest')
    sort = request.GET.get('sort', 'latest')
    
    # 정렬 기준에 따라 쿼리셋을 정렬합니다.
    if sort == 'latest':
        posts = Post.objects.all().order_by('-created_at')
    elif sort == 'rating':
        posts = Post.objects.all().order_by('-rating')
    elif sort == 'likes':
        posts = Post.objects.all().order_by('-likes')
    else:
        posts = Post.objects.all().order_by('-created_at')  # 기본값: 최신순
    
    context = {
        'posts': posts,
        'sort': sort
    }
    return render(request, 'posts/posts_list.html', context)

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
