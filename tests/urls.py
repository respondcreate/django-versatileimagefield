from django.conf import settings
from django.urls import include, path, re_path
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns = [
        re_path(
            r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}
        ),
        path('', include('django.contrib.staticfiles.urls')),
    ] + urlpatterns
