import time
import os
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from articles.models import Article, Tag
import schedule

def run_monthly_tasks():
    """Ежемесячный запуск генерации отчета и сбора статистики"""
    # Проверка даты: выполняется строго 24-го числа
    if datetime.now().day == 24:
        print(f"\n--- СТАРТ ЕЖЕМЕСЯЧНЫХ РАБОТ ({datetime.now().strftime('%d.%m.%Y %H:%M:%S')}) ---")
        
        # 1. ГЕНЕРАЦИЯ CSV-ОТЧЕТА
        filename = f"report_asutp_{datetime.now().strftime('%Y_%m_%d')}.csv"
        full_path = os.path.join(settings.BASE_DIR, filename)
        
        with open(full_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', 'Название', 'Автор', 'Дата публикации'])
            
            articles = Article.objects.all().select_related('author')
            for article in articles:
                writer.writerow([
                    article.id, 
                    article.title, 
                    article.author.username, 
                    article.pub_date.strftime('%d.%m.%Y')
                ])
        print(f"📄 CSV-отчет успешно сохранен по пути: {full_path}")
        
        # 2. СБОР СТАТИСТИКИ В КОНСОЛЬ
        total_articles = Article.objects.count()
        print(f"Всего статей в базе: {total_articles}")
        
        print("--- ВСЕ ЗАДАЧИ УСПЕШНО ВЫПОЛНЕНЫ ---\n")


class Command(BaseCommand):
    help = "Запуск ежемесячного планировщика отчетов и статистики АСУТП"

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Планировщик АСУТП успешно запущен."))
        
        # Настройка времени (измените "18:00" на нужное вам время)
        target_time = "17:29"
        schedule.every().day.at(target_time).do(run_monthly_tasks)
        
        self.stdout.write(f"Ожидание расписания (ежедневно в {target_time})...")

        # Импортируем schedule внутри метода, чтобы избежать конфликтов при старте Django
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\nПланировщик остановлен."))
