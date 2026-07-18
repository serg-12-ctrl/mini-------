from django.contrib import admin
from django.utils.html import format_html  # ДОБАВЛЕНО: для безопасной генерации HTML-ссылок
from django.urls import reverse            # ДОБАВЛЕНО: для динамической сборки URL-адресов
from .models import Article, Tag, SavedArticle, Comment, FAQ, Forum, Question

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'pub_date', 'is_public']
    list_editable = ['is_public']
    list_filter = ['pub_date', 'author', 'tags', 'is_public']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']

@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'saved_at']
    list_filter = ['saved_at', 'user', 'article']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    # Добавили 'short_text' для красоты и 'is_approved' для отображения галочки/крестика
    list_display = ['user', 'article', 'short_text', 'is_approved', 'created_at']
    # Добавили 'is_approved' в фильтры справа, чтобы легко находить неодобренные
    list_filter = ['is_approved', 'created_at', 'user', 'article']
    search_fields = ['text', 'user__username']
    
    # Регистрируем наше массовое действие
    actions = ['approve_comments']

    def short_text(self, obj):
        """Обрезает длинный текст комментария в таблице админки до 50 символов."""
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Текст комментария'

    def approve_comments(self, request, queryset):
        """Массово одобряет выбранные галочками комментарии."""
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'Успешно одобрено комментариев: {updated}.')
    
    # Текст, который появится в выпадающем списке действий
    approve_comments.short_description = 'Одобрить выбранные комментарии'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_published')
    list_editable = ('is_published',)

@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title']

# ИСПРАВЛЕНО: Заменили простую регистрацию на класс с выводом ссылки на сайт
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # Добавили 'view_on_site_link' в список отображаемых колонок
    list_display = ['title', 'forum', 'author', 'created_at', 'view_on_site_link']
    list_filter = ['created_at', 'forum', 'author']
    search_fields = ['title', 'content']

    def view_on_site_link(self, obj):
        """Создает кнопку-ссылку для мгновенного перехода к вопросу на самом сайте."""
        # Собираем точный URL-адрес страницы вопроса (имя маршрута взято из articles/urls.py)
        url = reverse('question_detail', kwargs={'question_id': obj.id})
        # Возвращаем красивую кнопку для панели управления
        return format_html('<a class="button" href="{}" target="_blank" style="background: #264b5d; color: #fff; padding: 4px 8px; border-radius: 4px; text-decoration: none;">Открыть ↗</a>', url)
    
    # Заголовок столбца в админке
    view_on_site_link.short_description = 'На сайте'
