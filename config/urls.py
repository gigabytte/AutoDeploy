'''
urls.py for base django project
Author: Dev Guys
Sub Author: Greg Brooks
'''
from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView # new
from django.conf.urls.static import static
from django.conf import settings

def isLoggedIn(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/accounts/dashboard')
    else:
        return login(request)

# base urls start at root of webiste ie . www.domain.com/dashboard
#accounts app handles all major url pointers
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('django.contrib.auth.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
