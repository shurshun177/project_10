from django.db import models
from django.contrib.auth.models import AbstractUser


# Надо исправить: Роли описаны в виде чойсов.
class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    USER_ROLES = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    )
    email = models.EmailField(unique=True)
    confirmation_code = models.CharField(
        max_length=99,
        blank=True,
        editable=False,
        null=True,
        unique=True
    )
    role = models.CharField(
        # Можно лучше: Тут обычно задают 9, как в moderator.
        # Я бы закладывался сразу с запасом
        max_length=20,
        choices=USER_ROLES,
        default=USER
    )
    bio = models.TextField(blank=True)

    class Meta:
        ordering = ('username',)

    # Можно лучше: можно добавить тут property для удобства
    @property
    def is_admin(self):
        # Надо исправить: Везде, где мы используем роли - не используем строки,
        # а используем константу
        return (
            self.role == User.ADMIN
            or self.is_superuser
            # Я тут не уверен, считается ли стафф "администратором Django"
            # по спеке, но будем считать, что да
            or self.is_staff
        )

    @property
    def is_moderator(self):
        return self.role == User.MODERATOR
