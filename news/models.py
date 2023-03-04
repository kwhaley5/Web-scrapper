from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    pass

class Query(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='User')
    website = models.CharField(max_length=30)
    search = models.CharField(max_length=64)
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} searched {self.search} on {self.website}"
    
class Article(models.Model):
    headline = models.CharField(max_length=256)
    body = models.CharField(max_length=5000)
    category = models.CharField(max_length=32)
    url = models.URLField(max_length=200)
    search = models.ForeignKey(Query, on_delete=models.CASCADE, related_name='Query')