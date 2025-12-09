from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignUpForm
from accounts.models import Profile

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()

            # Mise à jour du rôle
            role = form.cleaned_data['role']
            Profile.objects.filter(user=user).update(role=role)

            login(request, user)  
            return redirect('recipes:recipe_list')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})
