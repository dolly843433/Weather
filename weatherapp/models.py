from django.db import models

class WeatherData(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly define an auto-incrementing primary key
    city = models.CharField(max_length=100)
    temperature_kelvin = models.FloatField()
    temperature_celsius = models.FloatField()
    feels_like_kelvin = models.FloatField()
    feels_like_celsius = models.FloatField()
    main_condition = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=250)

    def __str__(self):
        return f"{self.city} - {self.main_condition} at {self.timestamp}"

class DailySummary(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly define an auto-incrementing primary key
    city = models.CharField(max_length=100)
    date = models.DateField()
    avg_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_temperature = models.FloatField()
    dominant_condition = models.CharField(max_length=50)

    class Meta:
        unique_together = ('city', 'date')  # Ensures one summary per city per day

    def __str__(self):
        return f"{self.city} - Summary for {self.date}"

class UserSettings(models.Model):
    id = models.AutoField(primary_key=True)  # Explicitly define an auto-incrementing primary key
    city = models.CharField(max_length=100)
    temperature_threshold = models.FloatField()
    condition_alert = models.CharField(max_length=50, blank=True, null=True)
    alert_enabled = models.BooleanField(default=True)

    def __str__(self):
        return f"Settings for {self.city} - User {self.user_id}"
