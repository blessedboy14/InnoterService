import uuid

from django.db import models


# Create your models here.


class Tag(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    name = models.CharField(max_length=120, unique=True)

    class Meta:
        ordering = ['-name']

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class Page(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField()
    user_id = models.UUIDField()
    image_url = models.CharField(max_length=350, default='https://placehold.co/220x120')
    tags = models.ManyToManyField(Tag)
    is_blocked = models.BooleanField(default=False)
    unblock_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def unblock(self):
        self.is_blocked = False
        self.unblock_date = None
        self.save()


class Followers(models.Model):
    page = models.ForeignKey(Page, related_name='followers', on_delete=models.CASCADE)
    user_id = models.UUIDField()


class Post(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True, primary_key=True
    )
    page = models.ForeignKey(Page, related_name='posts', on_delete=models.CASCADE)
    content = models.TextField()
    reply_to = models.UUIDField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']


class Likes(models.Model):
    user_id = models.UUIDField()
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
