from django.urls import path
from django.contrib.auth import views as auth_views # Добавьте этот импорт
from . import views
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.index, name='index'),
    path('articles/', RedirectView.as_view(url='/', permanent=True)),
    path('articles/', views.article_list, name='article_list'),
    path('article/<int:pk>/', views.article_detail, name='article_detail'),
    path('save/<int:pk>/', views.save_article, name='save_article'),
    path('unsave/<int:pk>/', views.unsave_article, name='unsave_article'),
    path('saved/', views.saved_articles, name='saved_articles'),
    #path('article/new/', views.article_create, name='article_create'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'), 
    path('export/csv/', views.export_report_csv, name='export_report_csv'),
    path('register/', views.register, name='register'),
    path('rules/', views.rules, name='forum_rules'),
    path('faq/', views.faq, name='faq_page'), 
    path('faq/<int:pk>/', views.faq_detail, name='faq_detail'),
    path('stats/', views.stats_view, name='stats'), 
    path('generate-report/', views.export_report_csv, name='generate_report'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
