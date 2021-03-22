from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin

try:
    from django.urls import re_path
except ImportError:
    from django.conf.urls import url as re_path


admin.autodiscover()

urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns = static(
        prefix=settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
        show_indexes=True
    ) + static(
        prefix=settings.STATIC_URL,
        document_root=settings.STATIC_ROOT,
    ) + urlpatterns