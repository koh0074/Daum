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

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
