

from django.db import models
from django.contrib.auth.models import User
class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    release_date = models.DateField()
    movie_id = models.IntegerField(default=1, unique=True)  # TMDb ID
    director = models.CharField(max_length=100)
    rating = models.DecimalField(max_digits=3, decimal_places=1)  # e.g., 8.7
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)

    def __str__(self):
        return self.title
class LikedMovie(models.Model):
    

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie_id = models.IntegerField()  
    movie_title = models.CharField(max_length=255)
    movie_poster = models.URLField()
    liked_at = models.DateTimeField(auto_now_add=True)
    comment = models.CharField(max_length=500, blank=True)
    def __str__(self):
        return f"{self.user.username} likes {self.movie_title}"
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    instagram = models.URLField(blank=True)
    bio = models.TextField(max_length=300, blank=True)

    def __str__(self):
        return self.user.username

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')