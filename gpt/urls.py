from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from .views import *


urlpatterns = [
    path("", home, name="home" ),
    path("chat_with_bot", chat_with_bot ,name="chat_with_bot"),
    path("authentication", authentication ,name="authentication"),
    path("handlelogout", handlelogout ,name="handlelogout"),
    path("session_chat", session_chat ,name="session_chat"),

]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += staticfiles_urlpatterns()
