from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    """Модель групп

    Аргументы:
    title: название группы.
    slug: slug группы
    description: описание группы.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        """Вернуть название группы"""
        return self.title


class Post(models.Model):
    """Модель постов

    Аргументы:
    text: текст поста.
    pub_date: дата публикации.
    author: автор поста(ссылка на модель User).
    group: группа, в которой был опубликован пост(ссылка на модель Group).
    """

    text = models.TextField(verbose_name='Текст поста',
                            help_text='Текст поста',)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа поста',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:30]

    class Meta:
        ordering = ['-pub_date']


class Comment(models.Model):
    """Модель коментариев"""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='post_comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author_comments'
    )
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:30]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='following')
