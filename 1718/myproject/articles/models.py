from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

class Article(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Содержание')
    image = models.ImageField(
        upload_to='articles/%Y/%m/%d/', 
        blank=True, 
        null=True, 
        verbose_name='Изображение'
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    pub_date = models.DateTimeField(default=timezone.now, verbose_name='Дата публикации')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    is_public = models.BooleanField(default=True, verbose_name='Публичная статья')

    def __str__(self):
        # Changed from self.name to self.title
        return self.title

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'pk': self.pk})

class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сохранения')

    def __str__(self):
        return f'{self.user.username} - {self.article.title}'

    class Meta:
        # Changed from unique = ('user', 'article') to unique_together
        unique_together = ('user', 'article')
        verbose_name = 'Сохранённая статья'
        verbose_name_plural = 'Сохранённые статьи'

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    def __str__(self):
        return f'Комментарий от {self.user.username} к статье {self.article.title}'

    class Meta:
        ordering = ['created_at']
        verbose_name='Комментарий'
        verbose_name_plural = 'Комментарии'
