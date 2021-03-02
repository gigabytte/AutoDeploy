from django.db import models

# Create your models here.

class Console(models.Model):
    POD_LOCATIONS = (
        ('Networking Lab', 0),
        ('Datacenter', 1),
    )
    console_name = models.CharField(max_length=30)
    pod_location = models.IntegerField(default=0)
    pod_number = models.IntegerField(default=0)
    console_ip_address = models.CharField(max_length=11, default='1.1.1.1')
    console_note = models.CharField(default='', max_length=100)

    def __str__(self):
        return self.console_name


class Device(models.Model):
    POD_LOCATIONS = (
        ('Networking Lab', 0),
        ('Datacenter', 1),
    )
    device_name = models.CharField(max_length=30)
    pod_location = models.IntegerField(default=0)
    pod_number = models.IntegerField(default=0)
    device_ip_address = models.CharField(max_length=11, default='1.1.1.1')
    device_mac_address = models.CharField(max_length=17, default='FF:FF:FF:FF:FF:FF')
    device_note = models.CharField(default='', max_length=100)

    def __str__(self):
        return self.windows_name
    