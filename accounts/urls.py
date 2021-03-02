from django.urls import path
from . import views as Views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('',Views.Home.as_view(), name='home'),
    #path('signup/', Views.SignUpView.as_view(), name='signup'), deprecated due to ldap authentication
    path('login/',Views.Login.as_view(), name='login'),
    path('dashboard/',Views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/profile/',Views.Profile.as_view(), name='profile'),
    path('dashboard/network/',Views.Network.as_view(), name='network'),
    path('dashboard/windows/',Views.Windows.as_view(), name='windows'),
    path('dashboard/scripts/',Views.Scripts.as_view(), name='scripts'),
    path('dashboard/equipment/',Views.Equipment.as_view(), name='equipment'),
    path('dashboard/equipment/add_device',Views.Equipment.as_view(), name='add_device'),
    path('dashboard/console/',Views.Console.as_view(), name='console'),
    path('dashboard/logout/',Views.Logout.as_view(), name='logout'),
]