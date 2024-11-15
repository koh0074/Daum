from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# 커스텀 User 모델
class User(AbstractUser):
    name = models.CharField(max_length=10, null=True, blank=True)
    nickname = models.CharField(max_length=20, null=True, blank=True)
    user_id = models.CharField(max_length=20, unique=True, null=True, blank=True)  # 사용자 고유 아이디 필드 추가

    def __str__(self):
        return self.user_id if self.user_id else self.username

class FriendRequest(models.Model):
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_requests', on_delete=models.CASCADE)
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"


