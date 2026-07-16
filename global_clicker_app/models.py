from django.db import models
from django.utils import timezone

class Click(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Click from {self.ip_address} at {self.timestamp}"


class PendingClick(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Pending click from {self.ip_address} at {self.timestamp}"
