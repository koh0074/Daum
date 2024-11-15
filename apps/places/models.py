from django.db import models

class Festival(models.Model):
    name = models.CharField(max_length=100)  # 축제 이름
    location = models.CharField(max_length=100)  # 축제 장소
    description = models.TextField()  # 축제 설명
    start_date = models.DateField()  # 시작 날짜
    end_date = models.DateField()  # 종료 날짜
    image = models.ImageField(upload_to='festival_images/', null=True, blank=True)  # 축제 이미지

    def __str__(self):
        return self.name
    
class TravelDestination(models.Model):
    name = models.CharField(max_length=100)  # 여행지 이름
    location = models.CharField(max_length=100)  # 여행지 위치
    description = models.TextField(null=True, blank=True)  # 여행지 설명
    image_url = models.URLField(null=True, blank=True)  # 여행지 이미지 URL

    def __str__(self):
        return self.name
