from django.contrib import admin
from .models import Article, Tag, SavedArticle, Comment, FAQ

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'pub_date', 'is_public']
    list_editable = ['is_public'] # Добавьте эту строку
    list_filter = ['pub_date', 'author', 'tags', 'is_public']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']

@admin.register(SavedArticle)
class SavedArticleAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'saved_at']
    list_filter = ['saved_at','user', 'article']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'article', 'created_at']
    list_filter = ['created_at', 'user', 'article']
    search_fields = ['text', 'user__username']




@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'is_published')
    list_editable = ('is_published',)