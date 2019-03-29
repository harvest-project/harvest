from django.conf import settings
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework.documentation import include_docs_urls

from home import views as home_views

plugin_patterns = [
    path('api/plugins/{}/'.format(plugin_name), include('plugins.{}.urls'.format(plugin_name)))
    for plugin_name in settings.PLUGINS]

main_patterns = [
    path('admin/', admin.site.urls),
    path('api/', include('home.urls')),
    path('api/settings/', include('settings.urls')),
    path('api/monitoring/', include('monitoring.urls')),
    path('api/torrents/', include('torrents.urls')),
    path('api/trackers/', include('trackers.urls')),
    path('docs/', include_docs_urls(title='Harvest API')),
]

# Append the main patterns, plugin patterns and a catch-all for frontend SPA URLs
urlpatterns = main_patterns + plugin_patterns + [re_path('', home_views.Index.as_view())]
