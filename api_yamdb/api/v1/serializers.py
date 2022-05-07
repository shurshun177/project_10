
from django.contrib.auth import get_user_model
from rest_framework import serializers

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        model = Review

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data

        user = self.context['request'].user
        # Надо исправить: эту валидацию часто пихают во вьюсет.
        # Логика должна лежать в сериализаторе. Логика валидации - особенно.
        title_id = (
            self.context['request'].parser_context['kwargs']['title_id']
        )
        if Review.objects.filter(author=user, title__id=title_id).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на данное произведение'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True
    )

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date',)
        model = Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        # Надо исправить: Тут и ниже по спеке не должно быть id в выдаче
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ('id',)
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        fields = '__all__'
        model = Title


class UserCreationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)

    # Надо исправить: данный валидатор должен быть тут, а не во вьюхе.
    def validate_username(self, value):
        """Проверяем, что нельзя создать пользователя с username = "me"
        и, что нельзя создать с одинаковым username."""
        username = value.lower()
        if username == 'me':
            raise serializers.ValidationError(
                'Пользователя с username="me" создавать нельзя.'
            )
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                f'Пользователь с таким username — {username} — уже существует.'
            )
        return value

    def validate_email(self, value):
        """Проверяем, что нельзя создать пользователя с одинаковым username."""
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                f'Пользователь с таким Email — {email} — уже существует.'
            )
        return value


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'role', 'email', 'first_name', 'last_name', 'bio')
