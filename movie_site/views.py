from django.db.models import Q
from django.shortcuts import render,redirect,get_object_or_404
from .models import Media,UserMedia,Genre,Favorite,Profile
from django.views.generic import ListView,UpdateView,DeleteView,CreateView
from django.urls import reverse_lazy
from django.conf import settings
import requests
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin,PermissionRequiredMixin
from .forms import UserMediaEditForm
from django.http import HttpResponseNotAllowed
from django.core.mail import send_mail
import asyncio
import aiohttp
from django.core.cache import cache
from asgiref.sync import sync_to_async
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User


# Create your views here.
class Home(ListView):
    template_name = 'movie_site/home.html'
    model = Media
    context_object_name = 'media_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Basic queries
        context['movies'] = Media.objects.filter(type='movie')[:50]
        context['shows'] = Media.objects.filter(type='tv')[:50]

        # Popular by rating
        context['popular_movies'] = Media.objects.filter(type='movie').order_by('-rating')[:15]
        context['popular_shows'] = Media.objects.filter(type='tv').order_by('-rating')[:15]

        # Get trending movies (most added to collections in last 30 days)
        trending_movies = Media.objects.filter(
            type='movie',
            user__added_at__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            recent_additions=Count('user')
        ).order_by('-recent_additions', '-rating')[:10]

        # Get trending TV shows (most added to collections in last 30 days)
        trending_shows = Media.objects.filter(
            type='tv',
            user__added_at__gte=timezone.now() - timedelta(days=30)
        ).annotate(
            recent_additions=Count('user')
        ).order_by('-recent_additions', '-rating')[:10]

        # If no trending content (no user activity in last 30 days), fallback to highest rated
        if not trending_movies:
            trending_movies = Media.objects.filter(type='movie').order_by('-rating')[:10]

        if not trending_shows:
            trending_shows = Media.objects.filter(type='tv').order_by('-rating')[:10]

        context['trending_movies'] = trending_movies
        context['trending_shows'] = trending_shows


        # User stats
        if self.request.user.is_authenticated:
            context['Watched_count'] = UserMedia.objects.filter(
                user=self.request.user, status='Watched'
            ).count()
            context['Watchlist_count'] = UserMedia.objects.filter(
                user=self.request.user, status='Watchlist'
            ).count()
            context['favorite_count'] = Favorite.objects.filter(
                user=self.request.user
            ).count()

        return context



class UpdateProfile(LoginRequiredMixin,UpdateView):
    model = Profile
    fields = ['bio','profile_pic']
    template_name = 'movie_site/update_profile.html'
    success_url = reverse_lazy('home')
    def get_object(self):
        return Profile.objects.get(user=self.request.user)



class AddMovie(LoginRequiredMixin,UserPassesTestMixin,CreateView):
    template_name = 'movie_site/add_movie.html'
    model = Media
    fields = ['name','description','poster','rating','release_date','trailer_url','type','genre']
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.request.user.is_staff

    def form_valid(self, form):
        rating = form.cleaned_data['rating']
        if rating is not None:
            if rating < 0 or rating > 10:
                form.add.error("rating must be between 0 and 10")
                return self.form_invalid(form)
        return super().form_valid(form)


class EditMovie(LoginRequiredMixin,PermissionRequiredMixin,UpdateView):
    template_name = 'movie_site/edit_movie.html'
    model = Media
    fields = ['name','description','rating','poster','release_date','trailer_url','type','genre']
    success_url = reverse_lazy('home')
    permission_required = 'movie_site.edit_media'

    def get_object(self, queryset=None):
        return Media.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        rating = form.cleaned_data['rating']
        if rating is not None:
            if rating < 0 or rating > 10:
                form.add.error("rating must be between 0 and 10")
                return self.form_invalid(form)
        return super().form_valid(form)

    # To allow staff to edit from the ui
    # def has_permission(self):
    #     return self.request.user.is_staff or super().has_permission()


class DeleteMovie(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model = Media
    success_url = reverse_lazy('home')
    template_name = 'movie_site/delete_page.html'

    def test_func(self):
        return self.request.user.is_staff


@login_required
def update_user_media(request, media_slug):
    media = get_object_or_404(Media, slug=media_slug)
    user_media = get_object_or_404(UserMedia, user=request.user, media=media)

    if request.method == "POST":
        form = UserMediaEditForm(request.POST, instance=user_media)
        if form.is_valid():
            # Save status, rating, review
            updated = form.save(commit=False)
            updated.save()

            # Save selected genres to the media
            selected_genres = form.cleaned_data['genres']
            media.genre.set(selected_genres)
            media.save()

            return redirect('user_media', status=user_media.status, type=media.type)
    else:
        # Preselect genres already assigned to this media
        form = UserMediaEditForm(instance=user_media)
        form.fields['genres'].initial = media.genre.all()

    context = {
        'form': form,
        'media': media,
        'user_media': user_media
    }
    return render(request, 'movie_site/edit_user_media.html', context)


class ModeratorViews(LoginRequiredMixin,PermissionRequiredMixin,ListView):
    model = UserMedia
    template_name = 'movie_site/moderator_view.html'
    context_object_name = 'user_media_list'
    permission_required = 'movie_site.view_user_media'
    paginate_by = 25

    def get_queryset(self):
        queryset = UserMedia.objects.all().order_by('-added_at')
        status = self.request.GET.get('status')
        type = self.request.GET.get('type')
        search = self.request.GET.get('q')

        if status:
            queryset = queryset.filter(status=status)
        if type:
            queryset = queryset.filter(media__type=type)
        if search:
            queryset = queryset.filter(Q(user__username__icontains=search) |
                                       Q(media__name__icontains=search)
                                       )
        return queryset



class ModeratorEdit(LoginRequiredMixin,PermissionRequiredMixin,UpdateView):
    model = UserMedia
    form_class = UserMediaEditForm
    template_name = 'movie_site/moderator_edit.html'
    permission_required = 'movie_site.edit_user_media'
    success_url = reverse_lazy('moderator_view')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.notify()
        return response

    def notify(self):
        subject = "Your media entry was updated"
        message = f"Dear {self.object.user.username}, your media '{self.object.media.name}' was edited by a moderator."
        from_email = f"MovieHub<{settings.EMAIL_HOST_USER}>"
        recipient_list = [self.object.user.email]
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            print(f"Failed to send email to {self.object.user.email}: {e}")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_media'] = self.object
        return context

@login_required
@permission_required('movie_site.delete_user_media',raise_exception=True)
def delete_user_content(request,usermedia_id):
    user_media = get_object_or_404(UserMedia,id=usermedia_id)

    subject = "Your media entry was deleted"
    message = f"Dear {user_media.user.username}, your media '{user_media.media.name}' was deleted by a moderator."
    from_email = f"MovieHub<{settings.EMAIL_HOST_USER}>"
    recipient_list = [user_media.user.email]

    user_media.delete()
    try:
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    except Exception as e:
        print(f"Failed to send email to {self.object.user.email}: {e}")
    return redirect('moderator_view')



@login_required
def delete_user_media(request, media_slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    media = get_object_or_404(Media,slug=media_slug)
    user_media = get_object_or_404(UserMedia, media=media, user=request.user)
    media_type = media.type
    status = user_media.status
    user_media.delete()
    return redirect('user_media', type=media_type,status=status)


@login_required
def remove_from_fav(request, media_slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    media = get_object_or_404(Media,slug=media_slug)
    user_media = get_object_or_404(Favorite, media=media, user=request.user)
    media_type = media.type
    user_media.delete()
    return redirect('favorites', type=media_type)


@login_required
def mark_as_watched(request, media_slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    media = get_object_or_404(Media,slug=media_slug)
    media_type = media.type
    user_media, created=UserMedia.objects.get_or_create(user=request.user, media=media,defaults={'status': 'Watched'})
    if not created:
        user_media.status = 'Watched'
        user_media.save()
    return redirect('user_media', type=media_type,status='Watched')


@login_required
def mark_as_watchlist(request, media_slug):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])
    media = get_object_or_404(Media,slug=media_slug)
    user_media = get_object_or_404(UserMedia, media=media, user=request.user)
    media_type = media.type
    user_media.status = 'Watchlist'
    user_media.save()
    return redirect('user_media', type=media_type,status='Watchlist')



# def search_movies(request):
#     query = request.GET.get('q')
#     movies = []
#
#     if query:
#         headers = {
#             "accept": "application/json",
#             "Authorization": f"Bearer {settings.TMDB_API_KEY}"
#         }
#
#         # Movie search
#         movie_url = "https://api.themoviedb.org/3/search/movie"
#         movie_params = {
#             'query': query,
#             'language': 'en-US',
#             'page': 1,
#             'include_adult': False
#         }
#         movie_response = requests.get(movie_url, params=movie_params, headers=headers)
#         movie_response.raise_for_status()
#         movie_data = movie_response.json()
#
#         for movie in movie_data.get('results', [])[:10]:
#             trailer_url = None
#
#             videos_response = requests.get(
#                 f"https://api.themoviedb.org/3/movie/{movie.get('id')}/videos",
#                 headers=headers
#             )
#             videos_response.raise_for_status()
#             videos_data = videos_response.json()
#
#             for video in videos_data.get('results', []):
#                 if video['site'].lower() == 'youtube' and video['type'].lower() == 'trailer':
#                     trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
#                     break
#
#             movies.append({
#                 'title': movie.get('title'),
#                 'description': movie.get('overview'),
#                 'poster': f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None,
#                 'release_date': movie.get('release_date'),
#                 'rating': movie.get('vote_average'),
#                 'id': movie.get('id'),
#                 'trailer_url': trailer_url,
#                 'type': 'movie'
#             })
#
#         # TV show search
#         tv_url = "https://api.themoviedb.org/3/search/tv"
#         tv_params = {
#             'query': query,
#             'language': 'en-US',
#             'page': 1,
#             'include_adult': False
#         }
#         tv_response = requests.get(tv_url, params=tv_params, headers=headers)
#         tv_response.raise_for_status()
#         tv_data = tv_response.json()
#
#         for show in tv_data.get('results', [])[:10]:
#             trailer_url = None
#
#             videos_response = requests.get(
#                 f"https://api.themoviedb.org/3/tv/{show.get('id')}/videos",
#                 headers=headers
#             )
#             videos_response.raise_for_status()
#             videos_data = videos_response.json()
#
#             for video in videos_data.get('results', []):
#                 if video['site'].lower() == 'youtube' and video['type'].lower() == 'trailer':
#                     trailer_url = f"https://www.youtube.com/watch?v={video['key']}"
#                     break
#
#             movies.append({
#                 'title': show.get('name'),
#                 'description': show.get('overview'),
#                 'poster': f"https://image.tmdb.org/t/p/w500{show.get('poster_path')}" if show.get('poster_path') else None,
#                 'release_date': show.get('first_air_date'),
#                 'rating': show.get('vote_average'),
#                 'id': show.get('id'),
#                 'trailer_url': trailer_url,
#                 'type': 'tv'
#             })
#
#         # Sort combined results by rating (descending)
#         movies.sort(key=lambda x: x['rating'] or 0, reverse=True)
#
#         # Limit to 15 total
#         movies = movies[:15]
#
#     context = {
#         'movies': movies,
#         'query': query,
#     }
#     return render(request, 'movie_site/search_movies.html', context)


# some things i don't know are here
def search_movies(request):
    query = request.GET.get('q')
    movies = []

    if query:
        # Check cache first
        cache_key = f"search_{query.lower().replace(' ', '_')}"
        cached_results = cache.get(cache_key)

        if cached_results:
            return render(request, 'movie_site/search_movies.html', {
                'movies': cached_results,
                'query': query,
            })

        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {settings.TMDB_API_KEY}"
        }

        # Fetch movies and TV shows in parallel
        movie_url = "https://api.themoviedb.org/3/search/movie"
        tv_url = "https://api.themoviedb.org/3/search/tv"

        params = {
            'query': query,
            'language': 'en-US',
            'page': 1,
            'include_adult': False
        }

        try:
            # Make parallel requests
            movie_response = requests.get(movie_url, params=params, headers=headers, timeout=10)
            tv_response = requests.get(tv_url, params=params, headers=headers, timeout=10)

            movie_response.raise_for_status()
            tv_response.raise_for_status()

            movie_data = movie_response.json()
            tv_data = tv_response.json()

            # Process movies (limit to 15 each)
            movies = process_movie_results(movie_data.get('results', [])[:12], 'movie', headers)
            tv_shows = process_tv_results(tv_data.get('results', [])[:8], 'tv', headers)

            # Combine and sort
            all_results = movies + tv_shows
            all_results.sort(key=lambda x: x['rating'] or 0, reverse=True)

            # Limit total results
            final_results = all_results[:20]

            # Cache for 10 minutes
            cache.set(cache_key, final_results, 600)

            context = {
                'movies': final_results,
                'query': query,
            }

        except requests.exceptions.RequestException as e:
            # Return empty results on error
            context = {
                'movies': [],
                'query': query,
                'error': 'Search service temporarily unavailable'
            }

    else:
        context = {
            'movies': [],
            'query': query,
        }

    return render(request, 'movie_site/search_movies.html', context)


def process_movie_results(movies, media_type, headers):
    """Process movie results without individual video calls"""
    results = []
    for movie in movies:
        # Get poster if available
        poster = f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get('poster_path') else None

        # Get trailer URL efficiently (you can remove this to make it faster)
        trailer_url = get_trailer_url(movie.get('id'), 'movie', headers) if movie.get('id') else None

        results.append({
            'title': movie.get('title'),
            'description': movie.get('overview'),
            'poster': poster,
            'release_date': movie.get('release_date'),
            'rating': round(movie.get('vote_average', 0), 1) if movie.get('vote_average') else None,
            'id': movie.get('id'),
            'trailer_url': trailer_url,
            'type': media_type
        })
    return results


def process_tv_results(shows, media_type, headers):
    """Process TV show results without individual video calls"""
    results = []
    for show in shows:
        poster = f"https://image.tmdb.org/t/p/w500{show.get('poster_path')}" if show.get('poster_path') else None

        # Get trailer URL efficiently
        trailer_url = get_trailer_url(show.get('id'), 'tv', headers) if show.get('id') else None

        results.append({
            'title': show.get('name'),
            'description': show.get('overview'),
            'poster': poster,
            'release_date': show.get('first_air_date'),
            'rating': round(show.get('vote_average', 0), 1) if show.get('vote_average') else None,
            'id': show.get('id'),
            'trailer_url': trailer_url,
            'type': media_type
        })
    return results


def get_trailer_url(media_id, media_type, headers):
    """Get trailer URL with timeout and error handling"""
    try:
        if media_type == 'movie':
            url = f"https://api.themoviedb.org/3/movie/{media_id}/videos"
        else:
            url = f"https://api.themoviedb.org/3/tv/{media_id}/videos"

        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        videos_data = response.json()

        for video in videos_data.get('results', []):
            if video['site'].lower() == 'youtube' and video['type'].lower() == 'trailer':
                return f"https://www.youtube.com/watch?v={video['key']}"

    except requests.exceptions.RequestException:
        # Silently fail - trailer is optional
        pass

    return None



class UserMediaListView(LoginRequiredMixin, ListView):
    model = UserMedia
    template_name = 'movie_site/user_watches.html'
    context_object_name = 'user_media'
    paginate_by = 12

    STATUS_MAP = {
        'watched': 'Watched',
        'watchlist': 'Watchlist',
    }

    def get_target_user(self):
        """Helper method to get the target user (either current user or viewed user)"""
        user_id = self.request.GET.get('user_id')
        if user_id:
            try:
                return User.objects.get(id=user_id)
            except User.DoesNotExist:
                return self.request.user
        return self.request.user

    def get_queryset(self):
        # Get status and type from URL parameters
        status_param = self.kwargs.get('status')
        media_type = self.kwargs.get('type')

        # Get filter parameters from GET request
        genres = self.request.GET.get('genres')
        rating = self.request.GET.get('rating')
        older = self.request.GET.get('older')
        search = self.request.GET.get('query')

        # Get the target user
        target_user = self.get_target_user()

        # Normalize status
        status = self.STATUS_MAP.get(status_param.lower()) if status_param else None

        queryset = UserMedia.objects.filter(
            user=target_user,
            status=status,
            media__type=media_type
        ).order_by('-added_at').select_related('media')

        # GENRE filter
        if genres:
            if "," in genres:
                genre_list = genres.split(",")
                queryset = queryset.filter(media__genre__slug__in=genre_list)
            else:
                queryset = queryset.filter(media__genre__slug=genres)

        # RATING filter
        if rating:
            try:
                queryset = queryset.filter(media__rating__gte=float(rating))
            except (ValueError, TypeError):
                # Handle invalid rating values
                pass

        # Sort oldest
        if older:
            queryset = queryset.order_by('added_at')

        # SEARCH
        if search:
            queryset = queryset.filter(
                Q(media__name__icontains=search)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        status = self.kwargs.get('status')
        media_type = self.kwargs.get('type')

        # Get the target user for counts
        target_user = self.get_target_user()

        # Add counts for the tab badges
        context['movie_count'] = UserMedia.objects.filter(
            user=target_user,
            status=status,
            media__type='movie'
        ).count()

        context['tv_count'] = UserMedia.objects.filter(
            user=target_user,
            status=status,
            media__type='tv'
        ).count()

        context['current_status'] = status
        context['current_type'] = media_type
        context['total_count'] = context['movie_count'] + context['tv_count']

        # Add the target user to context (useful for template to show whose list it is)
        context['target_user'] = target_user
        context['is_own_list'] = (target_user == self.request.user)

        return context



class DiscoverPeople(LoginRequiredMixin, ListView):
    model = User
    template_name = 'movie_site/discover_people.html'
    context_object_name = 'users'
    paginate_by = 30

    def get_queryset(self):
        search = self.request.GET.get('search','')
        queryset = User.objects.exclude(
            Q(id=self.request.user.id) |
            Q(id=1)
        )

        if search:
            queryset = queryset.filter(username__icontains=search)
        else:
            queryset = queryset.order_by('?')
        return queryset



class FavoriteListView(LoginRequiredMixin,ListView):
    model = Favorite
    template_name = 'movie_site/favorites.html'
    context_object_name = 'favorites'
    def get_queryset(self):
        media_type = self.kwargs.get('type')
        return Favorite.objects.filter(user=self.request.user,media__type=media_type).select_related('media')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_type = self.kwargs.get('type')

        # Add counts for the tab badges
        context['movie_count'] = Favorite.objects.filter(
            user=self.request.user,
            media__type='movie'
        ).count()

        context['tv_count'] = Favorite.objects.filter(
            user=self.request.user,
            media__type='tv'
        ).count()

        context['current_type'] = media_type
        context['total_count'] = context['movie_count'] + context['tv_count']

        return context



@login_required
def add_to_collection(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    title = request.POST.get('title')
    description = request.POST.get('description')
    release_date = request.POST.get('release_date')
    poster = request.POST.get('poster')
    trailer_url = request.POST.get('trailer_url')
    media_type = request.POST.get('type')
    rating = request.POST.get('rating')

    if title and release_date:
        media_added, created = Media.objects.get_or_create(
            name=title,
            defaults={
                'description': description or '',
                'release_date': release_date,
                'poster': poster or '',
                'trailer_url': trailer_url or '',
                'type': media_type,
                'rating': rating,
            }
        )

        UserMedia.objects.get_or_create(
            user=request.user,
            media=media_added,
            defaults={'status': 'Watchlist'}
        )

        return redirect('user_media', status='Watchlist', type=media_type)

    return redirect('search_movies')


@login_required
def add_to_favorite(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(['POST'])

    title = request.POST.get('title')
    description = request.POST.get('description')
    release_date = request.POST.get('release_date')
    poster = request.POST.get('poster')
    trailer_url = request.POST.get('trailer_url')
    media_type = request.POST.get('type')
    rating = request.POST.get('rating')

    if title and release_date:
        media_added, created = Media.objects.get_or_create(
            name=title,
            defaults={
                'description': description or '',
                'release_date': release_date,
                'poster': poster or '',
                'trailer_url': trailer_url or '',
                'type': media_type,
                'rating': rating,
            }
        )

        Favorite.objects.get_or_create(
            user=request.user,
            media=media_added,
        )

        return redirect('favorites', type=media_type)

    return redirect('search_movies')
