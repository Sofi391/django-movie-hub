from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import unidecode
from cloudinary.models import CloudinaryField


# Create your models here.
class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True,blank=True,max_length=120)
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode.unidecode(self.name))
            slug = base_slug
            counter = 1

            # Handle duplicate slugs
            while Genre.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Media(models.Model):
    name = models.CharField(max_length=100)
    release_date = models.DateField()
    description = models.TextField(null=True)
    poster = models.URLField(null=True)
    trailer_url = models.URLField(null=True)
    rating = models.FloatField(default=0)
    type = models.CharField(max_length=100,default='movie')
    slug = models.SlugField(unique=True,blank=True,max_length=120)

    genre = models.ManyToManyField(Genre,blank=True,related_name='media')

    class Meta:
        permissions = [
            ('edit_media','can edit media'),
            # ('view_media','can view media'),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(unidecode.unidecode(self.name))
            slug = base_slug
            counter = 1

            # Handle duplicate slugs
            while Media.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    profile_pic = CloudinaryField('image', default='default_zhxju7.png', blank=True, null=True)
    bio = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.user.username


class UserMedia(models.Model):
    user_choice = [
        ('Watched', 'Watched'),
        ('Watchlist', 'To Watch')
    ]
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='user_media')
    media = models.ForeignKey(Media,on_delete=models.CASCADE,related_name='user')
    status = models.CharField(max_length=20,choices=user_choice,default='Watchlist')
    rating = models.FloatField(default=None,null=True)
    review = models.TextField(blank=True,null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}  {self.media.name}"

    class Meta:
        unique_together = ('user','media')
        ordering = ['-added_at']
        permissions = [
            ('view_user_media','can view user media'),
            ('edit_user_media','can edit user media'),
            ('delete_user_media','can delete user media'),
        ]

class Favorite(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='favorites')
    media = models.ForeignKey(Media,on_delete=models.CASCADE,related_name='favorites')
    added_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user.username}  {self.media.name}"

    class Meta:
        unique_together = ('user','media')
        ordering = ['-added_at']


class Badge(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True,null=True)
    threshold = models.IntegerField()
    slug = models.SlugField(unique=True,blank=True,max_length=120)

    def __str__(self):
        return f"{self.name}-{self.threshold}"


class UserBadge(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name='badges')
    badge = models.ForeignKey(Badge,on_delete=models.CASCADE,related_name='user_badges')
    awarded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}-{self.badge.slug}"

    class Meta:
        unique_together = ('user','badge')


class Question(models.Model):
    text = models.TextField()
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=[('a','A'),('b','B'),('c','C'),('d','D')])
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class UserQuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.IntegerField()
    taken_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.score}"

