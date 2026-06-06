from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    # --- Статьи и системные страницы ---
    path('', views.index, name='index'),
    path('articles/', RedirectView.as_view(url='/', permanent=True)),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('save/<int:pk>/', views.save_article, name='save_article'),
    path('unsave/<int:pk>/', views.unsave_article, name='unsave_article'),
    path('saved/', views.saved_articles, name='saved_articles'),
    
    # --- Авторизация ---
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'), 
    path('register/', views.register, name='register'),
    
    # --- Разное ---
    path('export/csv/', views.export_report_csv, name='export_report_csv'),
    path('rules/', views.rules, name='forum_rules'),
    path('faq/', views.faq, name='faq_page'), 
    path('faq/<int:pk>/', views.faq_detail, name='faq_detail'),
    path('stats/', views.stats_view, name='stats'), 
    path('generate-report/', views.export_report_csv, name='generate_report'),
    
    # --- МАРШРУТЫ ФОРУМА (Добавлен префикс forums/) ---
    path('forums/', views.forum_list, name='forum_list'),  # Теперь форум доступен по адресу /forums/
    path('forums/<int:forum_id>/', views.forum_detail, name='forum_detail'),
    path('forums/<int:forum_id>/ask/', views.create_question, name='create_question'),
    
    # --- Вопросы и ответы ---
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    
    path('answer/<int:answer_id>/edit/', views.edit_answer, name='edit_answer'),
    path('answer/<int:answer_id>/delete/', views.delete_answer, name='delete_answer'),

    # --- Профили пользователей ---
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('article/create/', views.article_create, name='article_create'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
