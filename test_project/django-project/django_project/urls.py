from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.urls import path


urlpatterns = [
    *staticfiles_urlpatterns(),
    path('admin/', admin.site.urls),
]
