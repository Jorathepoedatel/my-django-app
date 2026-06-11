from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()


class Category(models.Model):
    name = models.CharField(max_length=40)


class Tag(models.Model):
    name = models.CharField(max_length=20)


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='articles'
    )
    tags = models.ManyToManyField(Tag, blank=True)

    def get_absolute_url(self):
        return reverse('blogapp:articles')