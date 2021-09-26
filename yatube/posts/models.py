from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    text = models.TextField(
        max_length=200,
        help_text='200 символов max',
        verbose_name='Текст',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        help_text='дата',
        verbose_name='Дата',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='автор',
        verbose_name='Автор',
        related_name='posts'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.CASCADE,
        blank=True, null=True,
        help_text='группа',
        verbose_name='Группа',
        related_name='posts'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'posts'
        verbose_name = 'posts'
        verbose_name_plural = 'посты'

    def __str__(self) -> str:
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        help_text='200 символов max',
        verbose_name='Название',
    )
    slug = models.SlugField(
        unique=True,
        max_length=200,
        help_text='текст',
        verbose_name='Пояснения',
    )
    description = models.TextField(
        help_text='Опишите группу',
        verbose_name='Описание',
    )

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'user'), name='unique_names'),
        ]

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.author}'
