from .models import Notification

def notifications_processor(request):
    """
    Автоматически добавляет непрочитанные уведомления текущего пользователя 
    в контекст любого HTML-шаблона сайта.
    """
    if request.user.is_authenticated:
        unread_notifications = request.user.notifications.filter(is_read=False)
        return {
            'unread_notifications': unread_notifications,
            'unread_notifications_count': unread_notifications.count()
        }
    return {
        'unread_notifications': [],
        'unread_notifications_count': 0
    }
