from django.urls import path, include
from rest_framework import routers

from notes.viewsets.auth import AuthViewSet
from notes.viewsets.category import CategoryViewSet
from notes.viewsets.note import NoteViewSet

app_name = 'api'


router = routers.DefaultRouter()
router.register('auth', AuthViewSet, basename='auth')
router.register('categories', CategoryViewSet, basename='categories')
router.register('notes', NoteViewSet, basename='notes')


urlpatterns = [
    path('', include(router.urls)),
]
