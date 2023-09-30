from django.urls import include, path
from rest_framework import routers

from users.views import UserViewSet

app_name = 'api'

v1_router = routers.DefaultRouter()

v1_router.register('users', UserViewSet, basename='users')
# v1_router.register('genres', GenreViewSet, basename='genres')
# v1_router.register('categories', CategoryViewSet, basename='categories')
# v1_router.register('titles', TitleViewSet, basename='titles')
# v1_router.register(
#     r'titles/(?P<title_id>\d+)/reviews',
#     ReviewViewSet,
#     basename='reviews'
# )
# v1_router.register(
#     r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
#     CommentViewSet,
#     basename='comments'
# )

delete_djoser_path_names = [
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
    if url.name not in delete_djoser_path_names
]

urlpatterns = [
    path('', include(v1_router_cleared)),
    path('auth/', include('djoser.urls.authtoken')),
]
