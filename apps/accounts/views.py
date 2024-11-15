from django.shortcuts import render, redirect
from apps.accounts.forms import SignupForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import auth

def main(request):
    return render(request, "base.html")

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True  # 필요 시 스태프 권한 추가
            user.save()
            auth.login(request, user)
            return redirect('accounts:user')
        else:
            # 폼이 유효하지 않을 경우 에러 메시지와 함께 다시 렌더링
            return render(request, 'accounts/signup.html', {'form': form, 'errors': form.errors})
    else:
        form = SignupForm()
        return render(request, 'accounts/signup.html', {'form': form})
    
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth.login(request, user)
            return redirect('accounts:user')
        else:
            context = {
                'form':form,
            }
            return render(request,
                        template_name='accounts/login.html',
                        context=context)
    else:
        form = AuthenticationForm()
        context = {
            'form': form,
        }
        return render(request, template_name='accounts/login.html', context=context)

def logout(request):
    auth.logout(request)
    return redirect('/')

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import FriendRequest

User = get_user_model()

@login_required
def search_user(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            # 검색한 유저 (로그인한 사용자 자신 제외)
            user = User.objects.get(username=user_id)
            if user == request.user:
                return JsonResponse({'error': '자신의 아이디입니다.'}, status=400)

            # 이미 친구인지 확인
            is_friend = FriendRequest.objects.filter(
                from_user=request.user, to_user=user, is_accepted=True
            ).exists() or FriendRequest.objects.filter(
                from_user=user, to_user=request.user, is_accepted=True
            ).exists()

            # 검색된 사용자의 정보를 반환
            return JsonResponse({
                'username': user.username,
                'user_id': user.id,
                'is_friend': is_friend
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': '해당 아이디를 가진 사용자가 없습니다.'}, status=404)
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=400)

@login_required
def send_friend_request(request, user_id):
    to_user = get_object_or_404(User, id=user_id)
    # 이미 친구 요청이 있는지 확인
    if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
        return redirect('accounts:friends_list')
    FriendRequest.objects.create(from_user=request.user, to_user=to_user)
    return redirect('accounts:friends_list')



# 받은 친구 요청 목록 보기
@login_required
def friend_requests(request):
    received_requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)
    return render(request, 'accounts/friend_requests.html', {'requests': received_requests})

# 친구 목록 보기
@login_required
def friends_list(request):
    friends = FriendRequest.objects.filter(from_user=request.user, is_accepted=True)
    return render(request, 'accounts/friends_list.html', {'friends': friends})

# 친구 요청 수락하기
@login_required
def accept_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        friend_request.is_accepted = True
        friend_request.save()
        return JsonResponse({'status': 'accepted'})
    return JsonResponse({'status': 'error'}, status=400)

# 친구 요청 거절하기
@login_required
def decline_friend_request(request, request_id):
    if request.method == 'POST':
        friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)
        friend_request.delete()
        return JsonResponse({'status': 'declined'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def get_friend_requests(request):
    received_requests = FriendRequest.objects.filter(to_user=request.user, is_accepted=False)
    data = [
        {
            'id': req.id,
            'from_user': req.from_user.username,
            'from_user_nickname': req.from_user.nickname
        }
        for req in received_requests
    ]
    return JsonResponse({'requests': data})

