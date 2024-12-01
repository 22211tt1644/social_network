from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.utils import timezone


User = get_user_model()

# Create your models here.
class Profile(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.OneToOneField(User,verbose_name='name', related_name='profile', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')
    bio = models.TextField(max_length=500, blank=True) 
    location = models.CharField(max_length=100, blank=True)
    friends = models.ManyToManyField(User, blank=True, related_name='friends_profiles')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.user.username} Profile'

    def __str__(self):
        return(str(self.user)) 

    def get_absolute_url(self):
        return reverse('home')

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_requests', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"

class FollowersCount(models.Model):
    user = models.ForeignKey(User, related_name="followed_user", on_delete=models.CASCADE)
    follower = models.ForeignKey(User, related_name="follower_user", on_delete=models.CASCADE)
    followed_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.follower} follows {self.user}"

class Post(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(null=True, blank=True, upload_to="images/")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post_date = models.DateTimeField(default=timezone.now)
    likes = models.ManyToManyField(User, blank=True, related_name='likes')
    shared_from = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='shared_posts'
    )

    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title + " | " + str(self.author)

    def get_absolute_url(self):
        return reverse('home')

    def get_owner_pp(self):
        return self.author.profile.avatar.url

    def profileid(self):
        return self.author.user.id

class Comment(models.Model):
    post=models.ForeignKey(Post,related_name="comments",on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f'{self.user.username} - {self.content[:20]}'

    def get_absolute_url(self):
        return reverse('post_detail', kwargs={'post_id': self.post_id})
    
    def total_likes(self):
        return self.likes.count()

class LikePost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return self.username
    
class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name="likes", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'comment')

    def __str__(self):
        return f"{self.user.username} likes {self.comment.content[:20]}"
    


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('reply', 'Reply'),
        ('follow', 'Follow'),
        ('add', 'Add'),
        ('friend', 'Friend'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, null=True, blank=True)  # optional
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.sender} - {self.notification_type} - {self.user}'
    
class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} to {self.receiver} at {self.timestamp}"
    
class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.code}"
    
class Group(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='group_images/', null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_groups")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

# Mô hình thành viên nhóm
class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.group.name}"

    class Meta:
        unique_together = ('group', 'user')  # Đảm bảo mỗi người chỉ có thể gia nhập nhóm 1 lần

# Mô hình tin nhắn trong nhóm
class MessageGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message by {self.user.username} in {self.group.name}"

# Mô hình yêu cầu mời bạn bè vào nhóm
class GroupInvitation(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="invitations")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invitations")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_invitations")
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('declined', 'Declined')], default='pending')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Invitation from {self.sender.username} to {self.receiver.username} for group {self.group.name}"
    
class BlockList(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocker')
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blocked')
    blocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')


