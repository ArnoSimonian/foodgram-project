from django.urls import include, path
from rest_framework import routers

from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import UserViewSet

app_name = 'api'

v1_router = routers.DefaultRouter()

v1_router.register('users', UserViewSet, basename='users')
v1_router.register('tags', TagViewSet, basename='tags')
v1_router.register('ingredients', IngredientViewSet, basename='ingredients')
v1_router.register('recipes', RecipeViewSet, basename='recipes')

djoser_path_names_to_delete = [
    'user-activation',
    'user-resend-activation',
    'user-reset-username',
    'user-reset-username-confirm',
    'user-reset-password',
    'user-reset-password-confirm',
    'user-set-username',
]

v1_router_cleared = [
    url for url in v1_router.urls
    if url.name not in djoser_path_names_to_delete
]

urlpatterns = [
    path('', include(v1_router_cleared)),
    path('auth/', include('djoser.urls.authtoken')),
]
