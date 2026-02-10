from django.contrib import admin
from .models import (Media, UserMedia, Genre, Favorite,
                     Profile,UserBadge,Badge,Question,
                     UserQuizAttempt,Notification)


# Register your models here.
@admin.register(Media)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'release_date', 'rating', 'trailer_url')  # show in list view
    search_fields = ('name',)

@admin.register(UserMedia)
class UserMediaAdmin(admin.ModelAdmin):
    list_display = ('id','user', 'media', 'rating',)
    search_fields = ('user', 'media')
    ordering = ('-added_at',)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'media')
    search_fields = ('user', 'media')
    ordering = ('added_at',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user', 'bio')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge')
    search_fields = ('user', 'badge')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name','description','slug','threshold')
    search_fields = ('name','slug')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'option_a', 'option_b', 'option_c','option_d','correct_option')
    search_fields = ('text',)

@admin.register(UserQuizAttempt)
class UserQuizAttemptAdmin(admin.ModelAdmin):
    list_display = ('user', 'score','taken_at')
    search_fields = ('user', 'score')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'sender__username','recipient__username','type')
    search_fields = ('title', 'sender__username', 'recipient__username')
