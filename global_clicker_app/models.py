from django.db import models

class Click(models.Model):
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Click from {self.ip_address} at {self.timestamp}"
