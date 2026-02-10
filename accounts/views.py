from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django import forms
from movie_site.models import Profile
from movie_site.services import inapp_notifications
from movie_site.tasks import send_email_task


# Create your views here.
class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email


class SignUpForm(CreateView):
    form_class = RegisterForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        response = super().form_valid(form)
        Profile.objects.create(user=self.object)
        login(self.request, self.object)
        title = 'Welcome to Movie Hub 🎬'
        content = f"""
Welcome to Movie Hub, {self.object.username}!

You’re all set 🎉
Start exploring movies, take quizzes, and earn badges as you go.

Head to your profile to track your progress and unlock new achievements!
        """
        type = 'System'
        inapp_notifications(self.object,type,title,content)

        subject = "Welcome to Movie Hub 🎉"
        message = f"""
Hi { self.object.username },

Welcome to Movie Hub!

Discover movies, take fun quizzes, and earn badges as you explore the platform.

Log in anytime to continue your journey and check out what’s new.

The Movie Hub Team 🎬
        """
        recipient_list = [self.object.email]
        send_email_task.delay(subject=subject, content=message, recipients=recipient_list)

        return response


