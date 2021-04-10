from django.urls import path
from . import views as Views
from django.contrib.auth.views import LogoutView

# All URLS for accounts app, all urls start @ base of appplication
urlpatterns = [
    path('',Views.Home.as_view(), name='home'),
    #path('signup/', Views.SignUpView.as_view(), name='signup'), deprecated due to ldap authentication
    path('login/',Views.Login.as_view(), name='login'),
    path('dashboard/',Views.Dashboard.as_view(), name='dashboard'),
    path('dashboard/profile/',Views.Profile.as_view(), name='profile'),
    path('dashboard/network/',Views.Network.as_view(), name='network'),
    path('dashboard/windows/',Views.Windows.as_view(), name='windows'),
    path('dashboard/scripts/all-scripts',Views.All_Scripts.as_view(), name='all_scripts'),
    path('dashboard/scripts/add-scripts',Views.Add_Scripts.as_view(), name='add_scripts'),
    path('dashboard/scripts/edit-scripts',Views.Edit_Scripts.as_view(), name='edit_scripts'),
    path('dashboard/scripts/delete_scripts',Views.Delete_Scripts.as_view(), name='delete_scripts'),
    path('dashboard/devices/all-devices/',Views.All_Devices.as_view(), name='all_devices'),
    path('dashboard/devices/equipment',Views.Equipment.as_view(), name='equipment'),
    path('dashboard/devices/console/',Views.Console.as_view(), name='console'),
    path('dashboard/logout/',Views.Logout.as_view(), name='logout'),
]