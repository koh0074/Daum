from django.conf import settings
from django.db import models
from django.utils import timezone

class Festival(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    image = models.ImageField(upload_to='festival_images/', null=True, blank=True)

    def __str__(self):
        return self.name
    
class TravelDestination(models.Model):
    name = models.CharField(max_length=100)  # 여행지 이름
    location = models.CharField(max_length=100)  # 여행지 위치
    description = models.TextField(null=True, blank=True)  # 여행지 설명
    image = models.ImageField(upload_to='travel_images/', null=True, blank=True)

    def __str__(self):
        return self.name

class FestivalBookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='place_bookmarks'
    )
    festival = models.ForeignKey(Festival, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'festival')

    def __str__(self):
        return f"{self.user.username} - {self.festival.name}"

    
class TravelBookmark(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    destination = models.ForeignKey(TravelDestination, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'destination')

    def __str__(self):
        return f"{self.user.username} - {self.destination.name}"
