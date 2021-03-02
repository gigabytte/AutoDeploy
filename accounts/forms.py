from django import forms
from .models import Console, Device

class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    password_repeat = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    #student_num = forms.CharField(widget=forms.NumberInput(attrs={'class':'form-control'}), required=False)

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control'}))

class AddConsoleForm(forms.ModelForm):
    class Meta:
        model = Console
        fields = ['console_name', 'pod_location', 'pod_number', 'console_ip_address', 'console_note']

class EditConsoleForm(forms.ModelForm):
    class Meta:
        model = Console
        fields = ['id', 'console_name', 'pod_location', 'pod_number', 'console_ip_address', 'console_note']


class DeleteConsoleForm(forms.ModelForm):
    class Meta:
        model = Console
        fields = ['console_name']

class AddDeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_name', 'pod_location', 'pod_number', 'device_ip_address', 'device_mac_address', 'device_note']

class EditDeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['id', 'device_name', 'pod_location', 'pod_number', 'device_ip_address', 'device_mac_address', 'device_note']

class DeleteDeviceForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = ['device_name']