from django.contrib import admin
from .models import Post, Tag, Comment, Like, Bookmark

# 간단하게 모든 모델 등록
admin.site.register(Post)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Bookmark)
