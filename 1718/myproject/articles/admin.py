from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.exceptions import NotRegistered
from django.utils.html import format_html  
from django.urls import reverse            
from .models import (
    Article, Tag, SavedArticle, Comment, FAQ, Forum, 
    Question, Profile, ModeratorAssignment, ExpertApplication, Answer
)

# =====================================================================
# ИНТЕГРАЦИЯ РОЛЕЙ В СТАНДАРТНУЮ КАРТОЧКУ ПОЛЬЗОВАТЕЛЯ (USER)
# =====================================================================

class ProfileInline(admin.StackedInline):
    """Позволяет редактировать роль профиля прямо внутри страницы пользователя."""
    model = Profile
    can_delete = False
    verbose_name_plural = 'Дополнительный профиль (Роль)'
    fields = ('role',)  # Выводим только поле выбора роли

# Перерегистрируем стандартный UserAdmin
try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Расширенная админка пользователей: выводит роль в общем списке 
    и добавляет блок управления ролями на страницу редактирования.
    """
    inlines = (ProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_role',)
    list_filter = BaseUserAdmin.list_filter + ('profile__role',)

    def get_role(self, obj):
        """
        ИЗМЕНЕНО: Безопасное получение роли. Если у старого пользователя 
        вдруг нет профиля, бэкенд создаст его на лету, предотвращая ошибку 
        RelatedObjectDoesNotExist при входе админа.
        """
        profile, created = Profile.objects.get_or_create(user=obj)
        return profile.get_role_display()
    get_role.short_description = 'Роль в системе'


# =====================================================================
# СУЩЕСТВУЮЩИЕ НАСТРОЙКИ АДМИНКИ ПРОЕКТА
# =====================================================================

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
    list_display = ['user', 'article', 'short_text', 'is_approved', 'created_at']
    list_filter = ['is_approved', 'created_at', 'user', 'article']
    search_fields = ['text', 'user__username']
    actions = ['approve_comments']

    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Текст комментария'

    def approve_comments(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'Успешно одобрено комментариев: {updated}.')
    approve_comments.short_description = 'Одобрить выбранные комментарии'


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_published')
    list_editable = ('is_published',)


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    search_fields = ['title']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'forum', 'author', 'created_at', 'view_on_site_link']
    list_filter = ['created_at', 'forum', 'author']
    search_fields = ['title', 'content']

    def view_on_site_link(self, obj):
        url = reverse('question_detail', kwargs={'question_id': obj.id})
        return format_html('<a class="button" href="{}" target="_blank" style="background: #264b5d; color: #fff; padding: 4px 8px; border-radius: 4px; text-decoration: none;">Открыть ↗</a>', url)
    view_on_site_link.short_description = 'На сайте'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['author', 'question', 'created_at']
    search_fields = ['content', 'author__username']


# =====================================================================
# УПРАВЛЕНИЕ ЗАЯВКАМИ И НАЗНАЧЕНИЯМИ МОДЕРАТОРОВ
# =====================================================================

@admin.register(ModeratorAssignment)
class ModeratorAssignmentAdmin(admin.ModelAdmin):
    """Панель закрепления модераторов за конкретными форумами техники."""
    list_display = ['user', 'forum', 'assigned_by', 'assigned_at']
    list_filter = ['forum', 'assigned_at', 'assigned_by']
    search_fields = ['user__username', 'forum__title']
    
    def save_model(self, request, obj, form, change):
        """При создании записи автоматически указывает администратора и меняет роль в профиле."""
        if not change:
            obj.assigned_by = request.user
        
        super().save_model(request, obj, form, change)
        
        # АВТОМАТИЗАЦИЯ: Находим профиль назначенного пользователя и ставим ему статус модератора
        profile = obj.user.profile
        if profile.role == 'user':  # Менять роль стоит только у обычных пользователей
            profile.role = 'moderator'
            profile.save()


@admin.register(ExpertApplication)
class ExpertApplicationAdmin(admin.ModelAdmin):
    """Панель проверки документов инженеров-экспертов."""
    list_display = ['user', 'specialization', 'status', 'created_at', 'view_documents_link']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'specialization']
    list_editable = ['status']
    actions = ['approve_applications', 'reject_applications']

    def view_documents_link(self, obj):
        if obj.documents:
            return format_html('<a href="{}" target="_blank" style="color: #264b5d; font-weight: bold; text-decoration: underline;">Смотреть документ 📄</a>', obj.documents.url)
        return "Нет документа"
    view_documents_link.short_description = 'Документы'

    def approve_applications(self, request, queryset):
        """Массовое одобрение: переводит статус заявки и обновляет роль в профиле."""
        for app in queryset:
            app.status = 'approved'
            app.save()
            
            # ИЗМЕНЕНО: Безопасное получение и обновление роли профиля
            profile, created = Profile.objects.get_or_create(user=app.user)
            profile.role = 'expert'
            profile.save()
        self.message_user(request, f'Выбранные заявки одобрены. Пользователи получили статус экспертов.')
    approve_applications.short_description = '👍 Одобрить заявки (сделать экспертами)'

    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, f'Выбранные заявки отклонены.')
    reject_applications.short_description = '👎 Отклонить выбранные заявки'
