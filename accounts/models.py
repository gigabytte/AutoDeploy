from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import uuid
import os

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


class Scripts(models.Model):
# generate random UUID for filename
    def get_file_path(instance, filename):
        ext = filename.split('.')[-1]
        filename = "%s.%s" % (uuid.uuid4(), ext)
        return os.path.join('scripts/', filename)

    script_name = models.CharField(max_length=30)
    script_version = models.FloatField(default=1.0)
    device_type = models.IntegerField(default=0)
    is_staff = models.BooleanField(default=False)
    script_note = models.CharField(default='', max_length=100)
    script_ext = models.CharField(null=True, blank=True, max_length=100)
    script_file = models.FileField(upload_to=get_file_path, null=True, blank=True, default='scripts/')

    def __str__(self):
        return self.script_name

    def save(self, *args, **kwargs):
        self.script_ext = self.script_file.file.content_type
        super().save(*args, **kwargs)

    def update_save(self, *args, **kwargs):
        super().save(*args, **kwargs)




""" Whenever ANY model is deleted, if it has a file field on it, delete the associated file too"""
@receiver(post_delete)
def delete_files_when_row_deleted_from_db(sender, instance, **kwargs):
    for field in sender._meta.concrete_fields:
        if isinstance(field,models.FileField):
            instance_file_field = getattr(instance,field.name)
            delete_file_if_unused(sender,instance,field,instance_file_field)
            
""" Delete the file if something else get uploaded in its place"""
@receiver(pre_save)
def delete_files_when_file_changed(sender,instance, **kwargs):
    # Don't run on initial save
    if not instance.pk:
        return
    for field in sender._meta.concrete_fields:
        if isinstance(field,models.FileField):
            #its got a file field. Let's see if it changed
            try:
                instance_in_db = sender.objects.get(pk=instance.pk)
            except sender.DoesNotExist:
                # We are probably in a transaction and the PK is just temporary
                # Don't worry about deleting attachments if they aren't actually saved yet.
                return
            instance_in_db_file_field = getattr(instance_in_db,field.name)
            instance_file_field = getattr(instance,field.name)
            if instance_in_db_file_field.name != instance_file_field.name:
                delete_file_if_unused(sender,instance,field,instance_in_db_file_field)

""" Only delete the file if no other instances of that model are using it"""    
def delete_file_if_unused(model,instance,field,instance_file_field):
    dynamic_field = {}
    dynamic_field[field.name] = instance_file_field.name
    other_refs_exist = model.objects.filter(**dynamic_field).exclude(pk=instance.pk).exists()
    if not other_refs_exist:
        instance_file_field.delete(False)


        