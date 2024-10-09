from django.urls import path
from .views import *

# Define Url patterns here for chat app.
urlpatterns = [
    path('', chat_view, name="home"),
]
