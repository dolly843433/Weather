from celery import shared_task
from .views import update_weather

@shared_task
def update_weather_task():
    # You can create a dummy request object if needed
    class Request:
        pass

    update_weather(Request())
