from django.db import models
from django.conf import settings

class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True, verbose_name="태그명")

    def __str__(self):
        return self.name


class Post(models.Model):
    title = models.CharField(max_length=100, verbose_name="제목")
    content = models.TextField(verbose_name="내용")
    location = models.CharField(max_length=100, verbose_name="위치", blank=True, null=True)
    rating = models.IntegerField(default=3, verbose_name="별점")  # 별점 필드
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name="태그")
    image = models.ImageField(upload_to='images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=False)  # 임시 저장 여부

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.author.username} - {self.content[:20]}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_bookmarks'
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} - {self.post.title}"