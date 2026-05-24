import csv
from datetime import datetime
from django.http import HttpResponse
from .models import Article

def create_csv_report(response_object=None):
    """
    Универсальная функция генерации CSV.
    Если передан response_object, пишет туда (для скачивания в браузере).
    Если не передан, создает физический файл на сервере (для планировщика).
    """
    # Если объекта ответа нет, создаем файл на сервере
    if response_object is None:
        filename = f"report_asutp_{datetime.now().strftime('%Y_%m_%d')}.csv"
        response_object = open(filename, 'w', encoding='utf-8', newline='')
        
    writer = csv.writer(response_object)
    # Заголовки отчета
    writer.writerow(['ID', 'Название', 'Автор', 'Дата публикации'])
    
    # Выгружаем статьи АСУТП из базы
    articles = Article.objects.all().select_related('author')
    for article in articles:
        writer.writerow([
            article.id, 
            article.title, 
            article.author.username, 
            article.pub_date.strftime('%d.%m.%Y')
        ])
        
    # Закрываем файл, если это запись на диск
    if not isinstance(response_object, HttpResponse):
        response_object.close()
        print(f"📄 CSV-отчет успешно сохранен на сервере как {filename}")
