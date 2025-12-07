from django import forms
from .models import UserMedia, Genre

class UserMediaEditForm(forms.ModelForm):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Select Genres"
    )

    class Meta:
        model = UserMedia
        fields = ['status', 'rating', 'review']  # base fields
