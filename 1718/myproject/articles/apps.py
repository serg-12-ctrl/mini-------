from django.apps import AppConfig


class ArticlesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'articles'

    # ДОБАВЛЕНО: Этот метод автоматически импортирует сигналы при запуске Django
    def ready(self):
        import articles.signals
