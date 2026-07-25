import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment

# Декоратор закомментирован. Функция больше НЕ вызывается автоматически при сохранении комментария.
# @receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    """Отправляет уведомление в Telegram при создании нового комментария."""
    print(f"--- Сработал сигнал! Комментарий создан: {created}, Одобрен: {instance.is_approved} ---")
    
    if created and not instance.is_approved:
        # Ваши проверенные и жестко вшитые данные:
        BOT_TOKEN = '8611946635:AAGzQHtRBE1qthjaUMKAtCOnbLVsDljAM4E'
        chat_id = '1670740429'
        
        # Ссылка ИСПРАВЛЕНА: добавлен поддомен api. и префикс /bot
        url = f"https://telegram.org{BOT_TOKEN}/sendMessage"
        
        print(f"--- Отправка запроса на правильный URL API: {url} ---")
        
        message = (
            f"📝 *Новый комментарий на модерацию!*\n\n"
            f"👤 *Пользователь:* {instance.user.username}\n"
            f"📰 *Статья:* {instance.article.title}\n"
            f"💬 *Текст:* {instance.text}\n\n"
            f"⏳ Одобрите его в панели администратора."
        )
        
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        try:
            # Отправляем JSON-данные напрямую в Telegram Bot API
            response = requests.post(url, json=payload, timeout=5)
            print(f"--- Ответ Telegram API: Статус {response.status_code}, Текст: {response.text} ---")
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка сети при отправке в Telegram: {e}")
