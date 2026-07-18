from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.db.models.functions import Lower
from datetime import datetime
from django.core.paginator import Paginator
from .models import Article, Tag, SavedArticle, Comment
from .forms import CommentForm
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .forms import CommentForm, ArticleForm  
#from django.http import HttpResponse, FileResponse
from django.http import HttpResponse, FileResponse, HttpResponseRedirect

#from .reports import generate_pdf_buffer  

from django.http import HttpResponse, FileResponse 
from django.shortcuts import render, redirect
from .models import SiteStatistic
from .models import FAQ

from .utils import create_csv_report


from django.contrib.auth.decorators import login_required
from .models import Forum, Question
from .forms import QuestionForm
from typing import Union
from .forms import CyrillicUserCreationForm
from django.contrib import messages
from .models import Article, Comment

from django.http import JsonResponse


@login_required
def generate_report_view(request) -> HttpResponse:
    """Генерирует и отдает пользователю аналитический отчет в формате CSV.

    Args:
        request (HttpRequest): Объект HTTP-запроса.

    Returns:
        HttpResponse: HTTP-ответ с прикрепленным файлом отчета.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="asutp_news_report.csv"'
    create_csv_report(response_object=response)
    return response




def create_article_view(request) -> HttpResponse:
    """Обеспечивает создание новой статьи и фиксирует действие в системной статистике.

    Args:
        request (HttpRequest): Объект HTTP-запроса.

    Returns:
        HttpResponse: Рендер страницы создания или редирект на главную.
    """
    if request.method == 'POST':
        if request.user.is_authenticated:
            SiteStatistic.objects.create(
                user=request.user,
                action="Добавил новую статью"
            )
        return redirect('index')
    return render(request, 'create_article.html')



def index(request) -> HttpResponse:
    """Формирует главную страницу со списком публичных статей, поиском, сортировкой и пагинацией.

    Args:
        request (HttpRequest): Объект HTTP-запроса.

    Returns:
        HttpResponse: Отреднеренный шаблон главной страницы с контекстом.
    """
    articles = Article.objects.filter(is_public=True).select_related('author')

    saved_ids = []
    saved_count = 0
    if request.user.is_authenticated:
        saved_ids = SavedArticle.objects.filter(user=request.user).values_list('article_id', flat=True)
        saved_count = len(saved_ids)

    query = request.GET.get('q', '').strip()
    if query:
        try:
            search_date = datetime.strptime(query, "%d.%m.%Y").date()
            articles = articles.filter(pub_date__date=search_date)
        except (ValueError, TypeError):
            articles = articles.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            ).distinct()

    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'author':
        articles = articles.order_by(Lower('author__username'), '-pub_date')
    elif sort_by == 'title':
        articles = articles.order_by(Lower('title'))
    elif sort_by == 'tags':
        articles = articles.order_by('tags__name').distinct()
    else:
        articles = articles.order_by('-pub_date')

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'saved_ids': saved_ids,
        'saved_count': saved_count,
        'query': query,
        'current_sort': sort_by,
        'login_form': AuthenticationForm(),
        'register_form': UserCreationForm(),
    }
    return render(request, 'articles/index.html', context)


def article_list(request) -> HttpResponse:
    """Выводит расширенный каталог статей с поддержкой фильтрации и закладок.

    Args:
        request (HttpRequest): Объект HTTP-запроса.

    Returns:
        HttpResponse: Отрендеренный шаблон каталога статей.
    """
    articles = Article.objects.filter(is_public=True).select_related('author')

    saved_ids = []
    if request.user.is_authenticated:
        saved_ids = SavedArticle.objects.filter(user=request.user).values_list('article_id', flat=True)

    query = request.GET.get('q', '').strip()
    if query:
        try:
            search_date = datetime.strptime(query, "%d.%m.%Y").date()
            articles = articles.filter(pub_date__date=search_date)
        except ValueError:
            articles = articles.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(author__username__icontains=query)
            )

    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'author':
        articles = articles.order_by(Lower('author__username'), '-pub_date')
    elif sort_by == 'title':
        articles = articles.order_by(Lower('title'))
    elif sort_by == 'tags':
        articles = articles.order_by('tags__name').distinct()
    else:
        articles = articles.order_by('-pub_date')  

    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'saved_ids': saved_ids,
        'query': query,
        'current_sort': sort_by
    }
    return render(request, 'articles/articles_list.html', context)



def article_detail(request, pk: int) -> HttpResponse:
    """Отображает полную статью, форму добавления и список комментариев.

    Args:
        request (HttpRequest): Объект HTTP-запроса.
        pk (int): Первичный ключ статьи.

    Returns:
        HttpResponse: Страница детального просмотра статьи.
    """
    article = get_object_or_404(Article, pk=pk)
    
    # ИЗМЕНЕНИЕ 1: Добавляем фильтр is_approved=True, чтобы отображать только одобренные комментарии
    comments = Comment.objects.filter(article=article, is_approved=True).select_related('user')

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.user = request.user 
            comment.save()
            
            # ИЗМЕНЕНИЕ 2: Добавляем уведомление для пользователя
            messages.success(
                request, 
                "Спасибо! Ваш комментарий отправлен на модерацию и появится на сайте после проверки администратором."
            )
            return redirect('article_detail', pk=pk)
    else:
        form = CommentForm()

    is_saved = False
    is_liked = False  # ДОБАВЛЕНО: переменная для статуса лайка текущего пользователя
    
    if request.user.is_authenticated:
        is_saved = SavedArticle.objects.filter(user=request.user, article=article).exists()
        # ДОБАВЛЕНО: проверяем, поставил ли лайк именно этот пользователь
        is_liked = article.likes.filter(id=request.user.id).exists()

    context = {
        'article': article,
        'comments': comments,
        'form': form,
        'is_saved': is_saved,
        'is_liked': is_liked,                  # ДОБАВЛЕНО в контекст
        'likes_count': article.likes.count()    # ДОБАВЛЕНО в контекст (общее число лайков)
    }
    return render(request, 'articles/article_detail.html', context)



@login_required
def save_article(request, pk: int) -> HttpResponseRedirect:
    """Добавляет выбранную статью в список избранного пользователя.

    Args:
        request (HttpRequest): Объект HTTP-запроса.
        pk (int): Первичный ключ сохраняемой статьи.

    Returns:
        HttpResponseRedirect: Перенаправление на исходную страницу.
    """
    article = get_object_or_404(Article, pk=pk)
    SavedArticle.objects.get_or_create(user=request.user, article=article)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', request.path))


@login_required
def unsave_article(request, pk: int) -> HttpResponseRedirect:
    """Удаляет выбранную статью из списка избранного пользователя.

    Args:
        request (HttpRequest): Объект HTTP-запроса.
        pk (int): Первичный ключ удаляемой статьи.

    Returns:
        HttpResponseRedirect: Перенаправление на исходную страницу.
    """
    article = get_object_or_404(Article, pk=pk)
    SavedArticle.objects.filter(user=request.user, article=article).delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', request.path))

@login_required
def saved_articles(request) -> HttpResponse:
    """Отображает персональный раздел пользователя со всеми сохраненными статьями.

    Args:
        request (HttpRequest): Объект HTTP-запроса.

    Returns:
        HttpResponse: Шаблон личного кабинета закладок.
    """
    saved_articles = SavedArticle.objects.filter(user=request.user).select_related('article')
    return render(request, 'articles/saved_articles.html', {'saved_articles': saved_articles})


from django.contrib.auth.decorators import user_passes_test # Добавьте импорт в самый верх файла

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from typing import Union

@user_passes_test(lambda u: u.is_superuser)
def article_create(request: HttpRequest) -> Union[HttpResponse, HttpResponseRedirect]:
    """Обрабатывает создание статьи.
    
    Returns:
        Union[HttpResponse, HttpResponseRedirect]: HTML-страница или редирект.
    """
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            return redirect('article_detail', pk=article.pk) # Возвращает HttpResponseRedirect
            
    else:
        form = ArticleForm()
        
    return render(request, 'articles/article_form.html', {'form': form}) # Возвращает HttpResponse


def custom_login_view(request) -> HttpResponse:
    """Аутентифицирует пользователя на сайте на основе стандартной формы Django.

    Args:
        request (HttpRequest): Объект HTTP-запроса.

    Returns:
        HttpResponse: Страница авторизации или редирект.
    """
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('index')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/register.html', {'form': form})



def register(request) -> HttpResponse:
    """Регистрирует нового пользователя в системе и автоматически авторизует его."""
    if request.method == 'POST':
        # Используем именно CyrillicUserCreationForm для применения регулярного выражения
        form = CyrillicUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index') 
    else:
        form = CyrillicUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

def rules(request):
    return render(request, 'articles/rules.html')




def faq(request):
    # Берем только те вопросы, у которых стоит галочка "Опубликовано"
    questions = FAQ.objects.filter(is_published=True)
    return render(request, 'articles/faq.html', {'questions': questions})

def faq_detail(request, pk):
    # Ищет вопрос по ID, если не находит — выдает ошибку 404 (Страница не найдена)
    question = get_object_or_404(FAQ, pk=pk, is_published=True)
    return render(request, 'articles/faq_detail.html', {'question': question})
import csv
from django.http import HttpResponse
from django.contrib.auth.models import User # Пример: берем данные пользователей

def export_report_csv(request):
    # Кодировка utf-8-sig важна для корректного отображения кириллицы в Excel
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="forum_report.csv"'

    writer = csv.writer(response)
    # Заголовки таблицы
    writer.writerow(['Имя пользователя', 'Email', 'Дата регистрации', 'Статус'])

    users = User.objects.all().order_by('-date_joined')

    for user in users:
        date_formatted = user.date_joined.strftime('%d.%m.%Y %H:%M')
        email = user.email if user.email else "не указан"
        status = "Администратор" if user.is_staff else "Пользователь"
        
        writer.writerow([user.username, email, date_formatted, status])

    return response
    
import json
from django.contrib.auth.models import User

from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Article, SavedArticle  # Убедитесь, что SavedArticle импортирована
from django.db.models import Count
from datetime import date

def stats_view(request):
    # ... ваши расчеты ...
    active_count = User.objects.filter(is_active=True).count()
    inactive_count = User.objects.filter(is_active=False).count()
    total = active_count + inactive_count

    # Считаем проценты здесь
    active_w = (active_count / total * 100) if total > 0 else 0
    inactive_w = (inactive_count / total * 100) if total > 0 else 0

    active_w = (active_count / total * 100) if total > 0 else 0
    inactive_w = (inactive_count / total * 100) if total > 0 else 0

    newest_user = User.objects.order_by('-date_joined').first()

    context = {
        'active': active_count,
        'inactive': inactive_count,
        'active_w': active_w,       # Передаем готовое число
        'inactive_w': inactive_w,   # Передаем готовое число
        'total_articles': Article.objects.count(),
        'today_articles': Article.objects.filter(pub_date__date=date.today()).count(),

         'newest_user': newest_user, 
    }
    return render(request, 'articles/stats.html', context)



from django.db.models import Count

# Получаем список имен и количество их статей
user_stats = User.objects.annotate(total_articles=Count('article')).filter(total_articles__gt=0)
labels = [user.username for user in user_stats]
data = [user.total_articles for user in user_stats]

import os
import io
from django.conf import settings
#from reportlab.pdfbase import pdfmetrics
#from reportlab.pdfbase.ttfonts import TTFont
#from reportlab.pdfgen import canvas
from django.http import FileResponse

def export_report_pdf(request):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    # --- УНИВЕРСАЛЬНЫЙ ПУТЬ К ШРИФТУ ---
    # Собирает путь: Корень_Проекта / static / fonts / arial.ttf
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'arial.ttf')
    
    try:
        # Регистрируем шрифт под именем 'RussianFont'
        pdfmetrics.registerFont(TTFont('RussianFont', font_path))
        p.setFont('RussianFont', 12)
    except:
        # Если шрифт не найден, используем стандартный (русский не будет виден)
        p.setFont('Helvetica', 12)

    # Теперь можно писать по-русски
    p.drawString(100, 750, "Отчет по пользователям портала АСУТП")
    
    # Пример вывода данных
    p.drawString(100, 730, f"Дата формирования: {os.path.getctime(font_path)}") # пример

    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='report.pdf')
def test_pdf_view(request):
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer) 
    p.drawString(100, 100, "Hello")
    p.showPage()
    p.save()
    buffer.seek(0)
    return FileResponse(buffer, filename="test.pdf")



# 1. Список всех форумов
def forum_list(request):
    forums = Forum.objects.all()
    #return render(request, 'forum/forum_list.html', {'forums': forums})
    return render(request, 'articles/forum_list.html', {'forums': forums})
# 2. Страница конкретного форума со списком вопросов
def forum_detail(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    questions = forum.questions.all().order_by('-created_at')
    #return render(request, 'forum/forum_detail.html', {'forum': forum, 'questions': questions})
    
    return render(request, 'articles/forum_detail.html', {'forum': forum, 'questions': questions})

# 3. Создание нового вопроса (только для авторизованных)
@login_required
def create_question(request, forum_id):
    forum = get_object_or_404(Forum, id=forum_id)
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.forum = forum       # Привязываем к текущему форуму
            question.author = request.user # Привязываем к вошедшему пользователю
            question.save()
            return redirect('forum_detail', forum_id=forum.id)
    else:
        form = QuestionForm()
        
    return render(request, 'articles/create_question.html', {'form': form, 'forum': forum})

from .models import Answer
from .forms import AnswerForm

# Детали вопроса + добавление ответа на той же странице
def question_detail(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    answers = question.answers.all().order_by('created_at') # Старые ответы вверху
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            # ИСПРАВЛЕНО: имя маршрута берем из urls.py (без слэшей и папок)
            return redirect('question_detail', question_id=question.id)
    else:
        form = AnswerForm()
        
    context = {
        'question': question,
        'answers': answers,
        'form': form
    }
    
    return render(request, 'articles/question_detail.html', context)


from django.core.exceptions import PermissionDenied

# Редактирование вопроса
@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.author != request.user:
        raise PermissionDenied  # Защита: чужой вопрос редактировать нельзя
        
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('question_detail', question_id=question.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'edit_question.html', {'form': form, 'question': question})

# Удаление вопроса
@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if question.author != request.user:
        raise PermissionDenied
        
    forum_id = question.forum.id
    if request.method == 'POST':
        question.delete()
        return redirect('forum_detail', forum_id=forum_id)
    return render(request, 'forum/delete_confirm.html', {'object': question, 'back_url': redirect('question_detail', question_id=question.id).url})

# Редактирование ответа
@login_required
def edit_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if answer.author != request.user:
        raise PermissionDenied
        
    if request.method == 'POST':
        form = AnswerForm(request.POST, instance=answer)
        if form.is_valid():
            form.save()
            return redirect('question_detail', question_id=answer.question.id)
    else:
        form = AnswerForm(instance=answer)
    return render(request, 'edit_answer.html', {'form': form, 'answer': answer})

# Удаление ответа
@login_required
def delete_answer(request, answer_id):
    answer = get_object_or_404(Answer, id=answer_id)
    if answer.author != request.user:
        raise PermissionDenied
        
    question_id = answer.question.id
    if request.method == 'POST':
        answer.delete()
        return redirect('question_detail', question_id=question_id)
    return render(request, 'forum/delete_confirm.html', {'object': answer, 'back_url': redirect('question_detail', question_id=question_id).url})



from django.contrib.auth.models import User
from django.contrib import messages

# Просмотр профиля (своих или чужих)
def user_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    
    # Получаем вопросы и ответы пользователя
    user_questions = profile_user.question_set.all().order_by('-created_at')
    user_answers = profile_user.answer_set.all().order_by('-created_at')
    
    context = {
        'profile_user': profile_user,
        'user_questions': user_questions,
        'user_answers': user_answers,
    }
    return render(request, 'forum/profile.html', context)

# Редактирование своего профиля
@login_required
def edit_profile(request):
    if request.method == 'POST':
        # Используем стандартные поля модели User
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Профиль успешно обновлен!')
        return redirect('user_profile', username=user.username)
        
    return render(request, 'forum/edit_profile.html')
from typing import List, Dict, Any, Optional

def format_tags(tags_queryset: Any) -> List[str]:
    """Преобразует QuerySet тегов в простой список строк.
    
    Args:
        tags_queryset: Данные из базы данных.
        
    Returns:
        List[str]: Список названий тегов.
    """
    return [tag.name for tag in tags_queryset]

def get_article_meta(article_id: int) -> Optional[Dict[str, Any]]:
    """Получает метаданные статьи в виде словаря, если статья существует.
    
    Args:
        article_id (int): Идентификатор статьи.
        
    Returns:
        Optional[Dict[str, Any]]: Словарь с данными или None, если статья не найдена.
    """
    try:
        article = Article.objects.get(id=article_id)
        return {
            "title": article.title,
            "views": 100,  # Пример статики
            "is_public": article.is_public
        }
    except Article.DoesNotExist:
        return None



def create_article_view(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # ... код сохранения статьи (допустим, получили её новый id = 42) ...
        
        # ВЫЗОВ ФУНКЦИИ: получаем метаданные для записи в историю действий
        meta = get_article_meta(article_id=42)
        if meta:
            SiteStatistic.objects.create(
                user=request.user,
                action=f"Опубликована статья: {meta['title']}"  # Используем данные из словаря
            )

@login_required
def toggle_article_like_json(request, pk: int) -> JsonResponse:
    """Добавляет/удаляет лайк статьи и возвращает JSON-ответ для JavaScript."""
    if request.method == "POST":
        article = get_object_or_404(Article, pk=pk)
        user = request.user
        
        if article.likes.filter(id=user.id).exists():
            article.likes.remove(user)
            liked = False
        else:
            article.likes.add(user)
            liked = True
            
        return JsonResponse({
            'liked': liked,
            'likes_count': article.likes.count()
        })
        
    return JsonResponse({'error': 'Invalid request method'}, status=400)