from django.db import models
from django.contrib.auth.models import User

from datetime import datetime, timedelta

class Asset(models.Model):
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.name} ({self.symbol})"

class Portfolio(models.Model):
    INTERVAL_CHOICES = [
        ("1m", "1 minute"),
        ("2m", "2 minutes"),
        ("5m", "5 minutes"),
        ("15m", "15 minutes"),
        ("30m", "30 minutes"),
        ("60m", "1 hour"),
        ("90m", "90 minutes"),
        ("1d", "Daily"),
        ("5d", "Every 5 days"),
        ("1wk", "Weekly"),
        ("1mo", "Monthly"),
        ("3mo", "Quarterly"),
    ]

    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    selected_assets = models.ManyToManyField("Asset")
    interval = models.CharField(choices=INTERVAL_CHOICES, max_length=5)
    start_date = models.DateTimeField(default=datetime(2010, 1, 1, 0, 0))
    end_date = models.DateTimeField(default=datetime.combine(datetime.today() - timedelta(days=1), datetime.min.time()))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"
