from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls

from home import views as home_views

plugin_patterns = [path(plugin.urls_prefix, include(plugin.urls_module_path))
                   for plugin in settings.PLUGINS]

main_patterns = [
    path('admin/', admin.site.urls),
    path('api/', include('home.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/monitoring/', include('monitoring.urls')),
    path('api/torrents/', include('torrents.urls', namespace='torrents')),
    path('api/trackers/', include('trackers.urls')),
    path('api/upload-studio/', include('upload_studio.urls')),
    path('api/image-cache/', include('image_cache.urls')),
    path('docs/', include_docs_urls(title='Harvest API')),
]

catch_all_patterns = [
    re_path('^api/', home_views.APINotFound.as_view()),
    re_path('^', home_views.Index.as_view()),
]

# Append the main patterns, plugin patterns and a catch-all for frontend SPA URLs
urlpatterns = main_patterns + plugin_patterns + catch_all_patterns
