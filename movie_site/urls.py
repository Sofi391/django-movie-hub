from django.urls import path
from .views import (Home, AddMovie, EditMovie, DeleteMovie,
                    search_movies, add_to_collection,
                    UserMediaListView, FavoriteListView,update_user_media,
                    delete_user_media,UpdateProfile,add_to_favorite,remove_from_fav,
                    mark_as_watched,mark_as_watchlist,ModeratorViews,ModeratorEdit,
                    delete_user_content,DiscoverPeople,get_user_badges,
                    get_badge_count,check_new_badges,add_to_watched,
                    QuizQuestionsListView,save_quiz_results,announcement_noti,
                    Notifications,mark_notification_read,mark_all_notifications_read,
                    delete_notification,health)

urlpatterns = [
    path('',Home.as_view(),name='home'),

    path('new_movie/',AddMovie.as_view(),name='new_movie'),
    path('movie/<slug:slug>/edit/',EditMovie.as_view(),name='edit_movie'),
    path('movie/<slug:slug>/delete/',DeleteMovie.as_view(),name='delete_movie'),

    path('moderator/view/',ModeratorViews.as_view(),name='moderator_view'),
    path('moderator/<int:pk>/edit/',ModeratorEdit.as_view(),name='moderator_edit'),
    path('moderator/<int:usermedia_id>/delete/',delete_user_content,name='moderator_delete'),

    path('search/',search_movies,name='search_movies'),

    path('add_to_collection/',add_to_collection,name='add_to_collection'),
    path('add_to_watched/',add_to_watched,name='add_to_watched'),
    path('add_to_favorite/',add_to_favorite,name='add_to_favorite'),
    path('my/favorites/<str:type>/',FavoriteListView.as_view(),name='favorites'),
    path('my/<str:status>/<str:type>/',UserMediaListView.as_view(),name='user_media'),

    path('edit/my/<slug:media_slug>/',update_user_media,name='edit_user_media'),
    path('delete/my_fav/<slug:media_slug>/',remove_from_fav,name='remove_from_favorite'),
    path('delete/my/<slug:media_slug>/',delete_user_media,name='delete_user_media'),

    path('mark/watched/<slug:media_slug>/',mark_as_watched,name='mark_watched'),
    path('mark_as/watchlist/<slug:media_slug>/',mark_as_watchlist,name='mark_watchlist'),

    path('profile/update/',UpdateProfile.as_view(),name='profile'),

    path('discover/people',DiscoverPeople.as_view(),name='discover_people'),

    path('badges/get-user-badges/', get_user_badges, name='get_user_badges'),
    path('badges/check-new-badges/', check_new_badges, name='check_new_badges'),
    path('badges/get-badge-count/', get_badge_count, name='get_badge_count'),

    path('notifications/',Notifications.as_view(),name='notifications'),

    path('weekly-quiz/',QuizQuestionsListView.as_view(),name='quiz'),
    path('save_results/',save_quiz_results,name='save_quiz_results'),

    path('announce/',announcement_noti,name='announcements'),
    path('notifications/<int:notification_id>/mark-read/', mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', delete_notification, name='delete_notification'),

    path('health/',health,name='health'),
]
