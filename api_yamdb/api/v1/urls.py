from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet, CommentViewSet, GenreViewSet, ReviewViewSet, TitleViewSet,
    UserViewSet, get_jwt_token, signup,
)

v1_router = DefaultRouter()
v1_router.register('genres', GenreViewSet, basename='genres')
v1_router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)
v1_router.register('titles', TitleViewSet, basename='titles')
v1_router.register(r'users', UserViewSet)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

# Надо исправить: Урлы с одинаковым префиксом выносим в
# отдельный список, чтобы сделать инклуд
auth_patterns = [
    path('signup/', signup, name='signup'),
    path('token/', get_jwt_token, name='get_token'),
]

urlpatterns = [
    path('auth/', include(auth_patterns)),
    path('', include(v1_router.urls))
]
