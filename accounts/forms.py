from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Profile

class SignUpForm(UserCreationForm):
    ROLE_CHOICES = (
        ('user', 'Utilisateur'),
        ('chef', 'Chef'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # créer automatiquement le profil
            Profile.objects.get_or_create(user=user)
        return user
