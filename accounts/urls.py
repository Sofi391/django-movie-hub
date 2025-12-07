from django.urls import path
from .views import SignUpForm
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('signup/',SignUpForm.as_view(),name='signup'),
    path('login/',auth_views.LoginView.as_view(template_name='accounts/login.html'),name='login'),
    path('logout/',auth_views.LogoutView.as_view(next_page='home'),name='logout'),
]