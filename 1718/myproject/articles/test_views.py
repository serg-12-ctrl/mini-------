import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Article

pytestmark = pytest.mark.django_db
User = get_user_model()

# --- Эти тесты у вас уже работают (оставляем без изменений) ---

def test_search_form(client):
    author = User.objects.create_user(username="testuser")
    Article.objects.create(title="Контроллеры АСУТП", author=author, content="Особый текст")
    Article.objects.create(title="Разработка Python", author=author, content="Другой текст")
    
    url = reverse('index')
    response = client.get(url, {'q': 'АСУТП'})
    html = response.content.decode('utf-8')
    assert "Контроллеры АСУТП" in html
    assert "Разработка Python" not in html

def test_sorting_by_date(client):
    author = User.objects.create_user(username="testuser")
    old_article = Article.objects.create(title="Старая новость", author=author)
    old_article.pub_date = timezone.now() - timedelta(days=5)
    old_article.save()
    
    Article.objects.create(title="Свежая новость", author=author)
    
    url = reverse('index')
    response = client.get(url, {'sort': 'date'})
    html = response.content.decode('utf-8')
    index_new = html.find("Свежая новость")
    index_old = html.find("Старая новость")
    assert index_new < index_old

# --- ИСПРАВЛЕННЫЕ ТЕСТЫ ---

def test_page_empty_list(client):
    """Тест: когда статей нет, карточки статей не отображаются."""
    url = reverse('index')
    response = client.get(url)
    
    assert response.status_code == 200
    html_content = response.content.decode('utf-8')
    # Проверяем, что в HTML нет карточек статей, так как список пуст
    assert "article-card" not in html_content

def test_favorites_icons_for_authenticated_user(client):
    """Тест избранного: проверяет отображение закладок для авторизованных пользователей."""
    author = User.objects.create_user(username="user1", password="password123")
    Article.objects.create(title="Статья для избранного", author=author, content="Текст")
    
    url = reverse('index')
    
    # Сценарий 1: Аноним без авторизации не должен видеть иконки закладок
    response = client.get(url)
    html_anon = response.content.decode('utf-8')
    assert "bi-bookmark" not in html_anon
    
    # Сценарий 2: Авторизуем пользователя
    client.login(username="user1", password="password123")
    
    # Если статья НЕ в избранном, должна отображаться пустая закладка (bi-bookmark)
    response = client.get(url)
    html_auth = response.content.decode('utf-8')
    assert "bi-bookmark" in html_auth
