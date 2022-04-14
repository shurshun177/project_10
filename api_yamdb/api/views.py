from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Category, Genre, Review, Title

from .filters import TitleFilter
from .permissions import (
    IsAdmin, IsAdminOrReadOnly, IsAuthorAdminModeratorOrReadOnly,
)
from .serializers import (
    CategorySerializer, CommentSerializer, ConfirmationCodeSerializer,
    GenreSerializer, ReviewSerializer, TitleReadSerializer,
    TitleWriteSerializer, UserCreationSerializer, UserSerializer,
)

User = get_user_model()


class CDLViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """
    A viewset that provides default `create()`, `destroy()`
    and `list()` actions.
    """
    # Можно лучше:
    # Заводим базовый класс для повторяющегося набор базовых классов
    pass


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    serializer = UserCreationSerializer(data=request.data)
    # Надо исправить:
    # Рассказываем про raise_exception, чтобы не делать вложенность и ифами
    serializer.is_valid(raise_exception=True)

    # Тут в спеке написано, что передается только email, поэтому студенты
    # часто вообще убирают username, но тк он везде в остальных местах
    # отдается отдельным полем, я делаю вывод, что он все-таки нужен.
    email = serializer.data['email']
    username = serializer.data['username']

    # Надо исправить: Рассказываем про get_or_create
    user, _ = User.objects.get_or_create(email=email, username=username)

    # Можно лучше: Тут студенты обычно придумывают разный зоопарк для
    # генерации токенов. Я бы рассказывал про uuid3/4 по желанию и
    # про вот этот стандартный механизм джанги
    confirmation_code = default_token_generator.make_token(user)

    # Надо исправить: Мейл отправителя должен быть задан константой,
    # которая зависит от DOMAIN_NAME
    send_mail(
        'Код подтверждения',
        f'Ваш код подтверждения: {confirmation_code}',
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    serializer = ConfirmationCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    username = serializer.data.get('username')
    confirmation_code = serializer.data.get('confirmation_code')
    user = get_object_or_404(User, username=username)

    if default_token_generator.check_token(user, confirmation_code):
        token = AccessToken.for_user(user)
        return Response(
            {'token': str(token)}, status=status.HTTP_200_OK
        )

    return Response({'confirmation_code': 'Неверный код подтверждения'},
                    status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'username'

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        # Надо исправить:
        # Здесь используем декоратор action вместо написания отдельной APIView
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorAdminModeratorOrReadOnly,
    ]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        # Можно лучше: Тут и ниже пользуем related_name
        reviews = title.reviews.all()
        return reviews

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get("title_id"))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorAdminModeratorOrReadOnly,
    ]

    def perform_create(self, serializer):
        # Надо исправить - тут и ниже проверяем, что это ревью на верный тайтл
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title__id=self.kwargs.get("title_id")
        )
        serializer.save(author=self.request.user, review=review)

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get("review_id"),
            title__id=self.kwargs.get("title_id")
        )
        # Можно лучше: Напоминаем про релейтед неймы
        return review.comments.all()


class CategoryViewSet(CDLViewSet):
    permission_classes = [IsAdminOrReadOnly, ]
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]


class TitleViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly, ]
    # Надо исправить: Здесь делаем аннотацию для рейтинга
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer

        return TitleWriteSerializer


class GenreViewSet(CDLViewSet):
    permission_classes = [IsAdminOrReadOnly, ]
    lookup_field = 'slug'
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=name', ]
