from django.urls import path
from . import views as Views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',Views.Home.as_view(), name='home'),
    path('signup/', Views.SignUpView.as_view(), name='signup'),
    path('dashboard/',Views.Dashboard.as_view(), name='dashboard'),
    path('logout/',Views.logout_view, name='logout'),
]