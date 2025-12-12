from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

APP_NAME = 'accounts'

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LoginView.as_view(template_name='accounts/logout.html'), name='logout'),
    

   
]
