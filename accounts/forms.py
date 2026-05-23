from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Profile

class SignUpForm(UserCreationForm):
    ROLE_CHOICES = (
        ('foodie', 'Foodie'),
        ('chef', 'Chef'),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        initial='foodie'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'role')

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Parlez-nous de vous...',
                'style': 'width:100%; padding:10px; border:2px solid #eee; border-radius:8px;'
            }),
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']