from django.contrib import admin
from .models import Media, UserMedia, Genre, Favorite,Profile


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