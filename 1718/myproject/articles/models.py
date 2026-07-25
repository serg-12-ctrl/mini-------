import os 
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from PIL import Image 

# =====================================================================
# НОВОЕ: Система Профилей, Ролей и Верификации (Внедрение)
# =====================================================================

class Profile(models.Model):
    """
    Профиль для расширения встроенной модели User дополнительными ролями.
    """
    ROLE_CHOICES = [
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
        ('expert', 'Проверенный эксперт'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="Пользователь")
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='user', 
        verbose_name="Роль в системе"
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль: {self.user.username} ({self.get_role_display()})"


class Forum(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название форума")
    description = models.TextField(verbose_name="Описание")

    class Meta:
        verbose_name = "Форум"
        verbose_name_plural = "Форумы"

    def __str__(self):
        return self.title


class ModeratorAssignment(models.Model):
    """
    Таблица привязки модераторов к конкретным разделам импортной техники (Форумам).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderated_forums', verbose_name="Модератор")
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='moderators', verbose_name="Раздел форума")
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_moderators', verbose_name="Кто назначил")
    assigned_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата назначения")

    class Meta:
        verbose_name = "Назначение модератора"
        verbose_name_plural = "Назначения модераторов"
        unique_together = ('user', 'forum')

    def __str__(self):
        return f"{self.user.username} модерирует {self.forum.title}"


class ExpertApplication(models.Model):
    """
    Модель заявок пользователей на получение статуса Эксперта по санкционной технике.
    """
    STATUS_CHOICES = [
        ('pending', 'Ожидает проверки'),
        ('approved', 'Одобрено'),
        ('rejected', 'Отклонено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expert_applications', verbose_name="Кандидат")
    specialization = models.TextField(verbose_name="Специализация по импортной технике")
    documents = models.FileField(upload_to='expert_docs/', verbose_name="Скан диплома/сертификата")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Статус заявки")
    comment = models.TextField(blank=True, null=True, verbose_name="Причина отказа (если отклонено)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата подачи")

    class Meta:
        verbose_name = "Заявка на верификацию"
        verbose_name_plural = "Заявки на верификацию"

    def __str__(self):
        return f"Заявка от {self.user.username} ({self.get_status_display()})"

# =====================================================================
# Существующий код проекта (С оптимизацией дублей и исправлением методов)
# =====================================================================

class Question(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='questions', verbose_name="Форум")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    title = models.CharField(max_length=250, verbose_name="Тема вопроса")
    content = models.TextField(verbose_name="Текст вопроса")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers', verbose_name="Вопрос")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор ответа")
    content = models.TextField(verbose_name="Текст ответа")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата ответа")

    class Meta:
        verbose_name = "Ответ на вопрос"
        verbose_name_plural = "Ответы на вопросы"

    def __str__(self):
        return f"Ответ от {self.author.username} к теме {self.question.title}"


class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Вопрос")
    answer = models.TextField(verbose_name="Ответ")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    class Meta:
        verbose_name = "Часто задаваемый вопрос"
        verbose_name_plural = "Часто задаваемые вопросы"

    def __str__(self):
        return self.question


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


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
    likes = models.ManyToManyField(User, related_name='liked_articles', blank=True, verbose_name='Лайки')

    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            img = Image.open(self.image.path)
            max_size = (800, 800)

            if img.height > max_size[1] or img.width > max_size[0]:
                img.thumbnail(max_size)
                img.save(self.image.path, quality=90)
            
            print(f"--- Файл: {self.image.name} ---")
            print(f"--- Разрешение: {self.image.width}x{self.image.height}px ---")
            print(f"--- Вес: {os.path.getsize(self.image.path) / 1024:.2f} Кб ---")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'pk': self.pk})


class SavedArticle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сохранения')

    class Meta:
        unique_together = ('user', 'article')
        verbose_name = 'Сохранённая статья'
        verbose_name_plural = 'Сохранённые статьи'

    def __str__(self):
        return f'{self.user.username} - {self.article.title}'


class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name='Статья')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_approved = models.BooleanField(default=False, verbose_name='Одобрен')

    class Meta:
        ordering = ['created_at']
        verbose_name='Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий от {self.user.username} к статье {self.article.title}'


class SiteStatistic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255)  
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Статистика'
        verbose_name_plural = 'Статистика'

    def __str__(self):
        username = self.user.username if self.user else "Гость"
        return f"{username} — {self.action} ({self.timestamp})"        


from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Автоматически создает профиль при регистрации НОВОГО пользователя."""
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Безопасно сохраняет профиль при обновлении данных пользователя."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        Profile.objects.create(user=instance)

# Поместите этот код строго в самый КОНЕЦ файла models.py
def get_or_create_profile(user_instance):
    try:
        return user_instance._profile_cache
    except AttributeError:
        # Автоматическое создание записи профиля "на лету" при любом входе/обращении
        profile, created = Profile.objects.get_or_create(user=user_instance)
        user_instance._profile_cache = profile
        return profile

User.profile = property(get_or_create_profile)


class Notification(models.Model):
    """
    Модель внутрисайтовых уведомлений для пользователей.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name="Получатель")
    text = models.CharField(max_length=255, verbose_name="Текст уведомления")
    link = models.CharField(max_length=200, blank=True, null=True, verbose_name="Ссылка для перехода")
    is_read = models.BooleanField(default=False, verbose_name="Прочитано")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата получения")

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ['-created_at'] # Свежие уведомления всегда вверху

    def __str__(self):
        return f"Уведомление для {self.user.username}: {self.text[:30]}..."
