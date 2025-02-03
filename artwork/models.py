from django.db import models
from django.conf import settings

class Artwork(models.Model):
    """AI 생성 이미지 작품"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)

    prompt = models.TextField(blank=True)
    negative_prompt = models.TextField(blank=True)
    ai_metadata = models.JSONField(default=dict)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
class ArtworkTag(models.Model):
    """작품 태그"""
    name = models.CharField(max_length=50, unique=True)
    artworks = models.ManyToManyField(Artwork, related_name='tags')

    def __str__(self):
        return self.name
    
class ArtworkComment(models.Model):
    """작품 댓글"""
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.artwork.title} by {self.user.username}"