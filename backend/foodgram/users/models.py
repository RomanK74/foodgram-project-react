from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

    ADMIN = 'admin'
    USER = 'user'

    ROLE = (
        (ADMIN, 'admin'),
        (USER, 'user'),
    )

    username = models.CharField(
        unique=True,
        null=False,
        max_length=150,
        verbose_name='Имя пользователя'
    )
    email = models.EmailField(
        unique=True,
        blank=True,
        null=False,
        max_length=254,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=150,
        null=False,
    )
    last_name = models.CharField(
        max_length=150,
    )
    role = models.CharField(
        max_length=15,
        choices=ROLE,
        default=USER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Пользаватель'
        verbose_name_plural = 'Пользователи'

    @property
    def is_admin(self):
        return (self.role == self.ADMIN or self.is_staff
                or self.is_superuser)

    def __str__(self):
        return self.username


class Subscribtion(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Пользователь',
        on_delete=models.CASCADE,
        null=False,
        related_name='subscriber'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        null=True,
        related_name='author',
    )

    class Meta:
        verbose_name = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=["user", "author"],
                                    name="followed_author")
        ]
