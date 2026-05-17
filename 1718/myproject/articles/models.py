from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from PIL import Image 
import os 




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

    def save(self, *args, **kwargs):
        # Сначала сохраняем объект, чтобы файл записался на диск
        super().save(*args, **kwargs)

        if self.image:
            # Открываем сохраненное изображение
            img = Image.open(self.image.path)

            # Задаем максимальные желаемые размеры (например, 800x800)
            max_size = (800, 800)

            # Проверяем, превышает ли картинка заданные размеры
            if img.height > max_size[1] or img.width > max_size[0]:
                # Метод thumbnail пропорционально сжимает картинку без искажений
                img.thumbnail(max_size)
                # Перезаписываем файл в том же качестве
                img.save(self.image.path, quality=90)
            
        
        if self.image:
            # Выводим размеры ДО или ПОСЛЕ сжатия
            print(f"--- Файл: {self.image.name} ---")
            print(f"--- Разрешение: {self.image.width}x{self.image.height}px ---")
            print(f"--- Вес: {os.path.getsize(self.image.path) / 1024:.2f} Кб ---")


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

class SiteStatistic(models.Model):
    # Связываем запись статистики с конкретным пользователем
    # null=True и blank=True нужны, если статистика может собираться для гостей
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255)  # Например: "Создал статью", "Зашел на сайт"
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Если пользователь есть, выводим его логин, иначе — "Гость"
        username = self.user.username if self.user else "Гость"
        return f"{username} — {self.action} ({self.timestamp})"        
