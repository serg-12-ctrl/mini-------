import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Article

# Даем тестам доступ к базе данных
pytestmark = pytest.mark.django_db

User = get_user_model()

def test_page_with_items(client):
    """Тест: когда статьи есть, они рендерятся в шаблоне."""
    # Создаем обязательного автора
    author = User.objects.create_user(username="testuser", password="password123")
    
    # Создаем тестовую статью со всеми необходимыми полями для шаблона
    Article.objects.create(
        title="Уникальный заголовок АСУТП", 
        author=author,
        content="Это тестовое содержимое для проверки фильтров шаблона."
    )
    
    # Переходим на главную страницу
    url = reverse('index')
    response = client.get(url)
    
    assert response.status_code == 200
    # Проверяем наличие заголовка и класса карточки статьи
    html_content = response.content.decode('utf-8')
    assert "Уникальный заголовок АСУТП" in html_content
    assert "article-card" in html_content

def test_page_empty_list(client):
    """Тест: когда статей нет, карточки статей не отображаются."""
    # Оставляем базу данных пустой
    url = reverse('index')
    response = client.get(url)
    
    assert response.status_code == 200
    # Так как блока {% empty %} в шаблоне нет, проверяем, 
    # что на странице отсутствует класс карточки статьи
    html_content = response.content.decode('utf-8')
    assert "article-card" not in html_content
