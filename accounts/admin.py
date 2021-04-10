from django.contrib import admin
from .models import *

# Register your models to be viewed in admin console page
admin.site.register(Console)
admin.site.register(Scripts)
admin.site.register(Device)