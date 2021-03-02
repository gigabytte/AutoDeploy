from accounts.models import Console, Device
from django.shortcuts import render, redirect
from django.views import generic, View
from django.views.generic import TemplateView
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.template import loader
from .forms import RegisterForm, LoginForm, AddDeviceForm, AddConsoleForm, DeleteConsoleForm, EditConsoleForm, AddDeviceForm, EditDeviceForm, DeleteDeviceForm
from django.template.response import TemplateResponse
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from itertools import chain


def superuser_required():
    def wrapper(wrapped):
        class WrappedClass(UserPassesTestMixin, wrapped):
            def test_func(self):
                return self.request.user.is_superuser

        return WrappedClass
    return wrapper

# this class is being deprecated in farvour of LDAP authication contexit()rol
class SignUpView(View):

    def get(self, request):
        template = 'registration/signup.html'
        form = RegisterForm()
        return render(request, template, {'form': form})
    def post(self, request):
        template = 'registration/signup.html'
        # create a form instance and populate it with data from the request:
        form = RegisterForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Username already exists.'
                })

            elif form.cleaned_data['password'] != form.cleaned_data['password_repeat']:
                return render(request, template, {
                    'form': form,
                    'error_message': 'Passwords do not match.'
                })
            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                return render(request, template, {
                    'form': form,
                    'error_message': 'Email already exists.'
                })
            else:
                # Create the user:
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password']
                )
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                # redirect to login page:
                return HttpResponseRedirect('/login')

class Login(View):
    def get(self, request):
        if not request.user.is_authenticated:
            template = 'registration/login.html'
            form = LoginForm()
            return render(request, template, {'form': form})
        else:
            return redirect('dashboard')

    def post(self, request):
        form = LoginForm(request.POST)
        blank_form = LoginForm()
        template = 'registration/login.html'
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']        
            auth = LDAPBackend()
            user = auth.authenticate(self, username=username, password=password)
            if user is not None:
                print('signed in successfully')
                login(request, user)
                return redirect('dashboard')
            else:
                return render(request, template, {
                    'form': blank_form,
                    'message': 'Username or Password Wrong'
                })

        else:
            print('Forum failed')
            return render(request, template, {
                    'form': blank_form,
                    'message': 'Forum error contact admin'
            })

class Home(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            return redirect('dashboard')

class Profile(View):
    def get(self, request):
        args = {}
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            userEmail = request.user.email
            userFirstName = request.user.first_name
            userLastName = request.user.last_name
            args['user_firstname'] = userFirstName
            if not userFirstName:
                args['user_firstname'] = request.user.username
            args['user_lastname'] = userLastName
            args['user_email'] = userEmail

            template = loader.get_template('user/profile.html')
            return TemplateResponse(request, template, args)

class Dashboard(LoginRequiredMixin, View):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):

        template = loader.get_template('user/dashboard.html')
        return HttpResponse(template.render({}, request))

class Network(LoginRequiredMixin, View):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):

        template = loader.get_template('user/network.html')
        return HttpResponse(template.render({}, request))

class Windows(LoginRequiredMixin, View):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        args = {}

        template = loader.get_template('user/windows.html')
        return TemplateResponse(request, template, args)

@superuser_required()
class Equipment(LoginRequiredMixin, generic.ListView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/equipment.html'
    model = Device
    
    def get_queryset(self):
     
        if self.request.GET.get('device_name'):
            self.selectedDeviceDetails = self.model.objects.get(pk=self.request.GET.get('device_name'))
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        if self.request.GET.get('device_name'):
            kwargs['device_details'] = self.selectedDeviceDetails
        if 'add_device' not in kwargs:
            kwargs['add_device'] = AddDeviceForm()
        if 'delete_device' not in kwargs:
            kwargs['delete_device'] = DeleteDeviceForm()
        if 'edit_device' not in kwargs:
            kwargs['edit_device'] = EditDeviceForm()
        
        return kwargs

    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'add_device' in request.POST:
            addDeviceForm = AddDeviceForm(request.POST)
            if addDeviceForm.is_valid():

                podNumberSelected = addDeviceForm.cleaned_data['pod_number']
                podLocationSelected = addDeviceForm.cleaned_data['pod_location']
                deviceIPAdressAdded = addDeviceForm.cleaned_data['device_ip_address']
                deviceMACAdressAdded = addDeviceForm.cleaned_data['device_mac_address']
                read_podLocationSelected = 'Networking Lab' if podLocationSelected == 0 else 'Datacenter'
   
                if not self.model.objects.filter(pod_number=podNumberSelected).filter(pod_location=podLocationSelected):
                    print('Added new Console to DB')
                    if not self.model.objects.filter(device_ip_address=deviceIPAdressAdded).filter(pod_location=podLocationSelected):
                        if not self.model.objects.filter(device_mac_address=deviceMACAdressAdded).filter(pod_location=podLocationSelected):
                            addDeviceForm.save()
                            messages.success(request, 'Successfully added new Device')
                        else:
                            messages.info(request, 'Deteted Duplicate MAC Address with another Device, please try again')
                            print('Failure to perform request, possible duplicate Device MAC Address')                        
                    else:
                        messages.info(request, 'Deteted Duplicate IP Address with another Device, please try again')
                        print('Failure to perform request, possible duplicate Device IP Address')
                else:
                    print('Unable to process Device Add Request due to possible duplicate entry problem')
                    messages.info(request, 'A Device is already asscoaited with Pod Number %s Located in %s , please try again or delete old Device first.' % (podNumberSelected, read_podLocationSelected))
            else:
                print('invalid Device form')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('equipment')

        elif 'delete_device' in request.POST:
            deleteDeviceForm = DeleteDeviceForm(request.POST)

            if deleteDeviceForm.is_valid():
                deviceID = deleteDeviceForm.cleaned_data['device_name']

                self.model.objects.filter(id=deviceID).delete()

                messages.success(request, 'Successfully deleted Device')
                print('Successfuly Device console')

            else:
                print('delete Device not valid')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('equipment')

        elif 'edit_device' in request.POST:
            editDeviceForm = EditDeviceForm(request.POST)

            if editDeviceForm.is_valid():
                editDeviceObject = self.model.objects.get(id=self.request.GET.get('device_name'))
                editDeviceObject.device_name = editDeviceForm.cleaned_data['device_name']
                editDeviceObject.pod_number = editDeviceForm.cleaned_data['pod_number']
                editDeviceObject.pod_location = editDeviceForm.cleaned_data['pod_location']
                editDeviceObject.device_ip_address = editDeviceForm.cleaned_data['device_ip_address']
                editDeviceObject.device_mac_address = editDeviceForm.cleaned_data['device_mac_address']
                editDeviceObject.device_note = editDeviceForm.cleaned_data['device_note']

                editDeviceObject.save()

                messages.success(request, 'Successfully edited Device')
                print('Successfuly edited device')

            else:
                print('edit device not valid')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('equipment')

        return redirect('equipment')

@superuser_required()
class Console(LoginRequiredMixin, generic.ListView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/console.html'
    model = Console
    
    def get_queryset(self):
     
        if self.request.GET.get('console_name'):
            self.selectedConsoleDetails = self.model.objects.get(pk=self.request.GET.get('console_name'))
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        if self.request.GET.get('console_name'):
            kwargs['console_details'] = self.selectedConsoleDetails
        if 'add_console' not in kwargs:
            kwargs['add_console'] = AddConsoleForm()
        if 'delete_console' not in kwargs:
            kwargs['delete_console'] = DeleteConsoleForm()
        if 'edit_console' not in kwargs:
            kwargs['delete_console'] = EditConsoleForm()
        
        return kwargs

    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'add_console' in request.POST:
            addConsoleForm = AddConsoleForm(request.POST)
            if addConsoleForm.is_valid():

                podNumberSelected = addConsoleForm.cleaned_data['pod_number']
                podLocationSelected = addConsoleForm.cleaned_data['pod_location']
                consoleIPAdressAdded = addConsoleForm.cleaned_data['console_ip_address']
                read_podLocationSelected = 'Networking Lab' if podLocationSelected == 0 else 'Datacenter'
   
                if not self.model.objects.filter(pod_number=podNumberSelected).filter(pod_location=podLocationSelected):
                    print('Added new Console to DB')
                    if not self.model.objects.filter(console_ip_address=consoleIPAdressAdded).filter(pod_location=podLocationSelected):
                        addConsoleForm.save()
                        messages.success(request, 'Successfully added new Console')
                    else:
                        messages.info(request, 'Deteted Duplicate IP Address with another Console, please try again')
                        print('Failure to perform request, possible duplicate Console IP Address')
                else:
                    print('Unable to process Console Add Request due to possible duplicate entry problem')
                    messages.info(request, 'A Console is already asscoaited with Pod Number %s Located in %s , please try again or delete old Console Manager first.' % (podNumberSelected, read_podLocationSelected))
            else:
                print('invalid console form')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('console')

        elif 'delete_console' in request.POST:
            deleteConsoleForm = DeleteConsoleForm(request.POST)

            if deleteConsoleForm.is_valid():
                consoleID = deleteConsoleForm.cleaned_data['console_name']

                self.model.objects.filter(id=consoleID).delete()

                messages.success(request, 'Successfully deleted Console')
                print('Successfuly delete console')

            else:
                print('delete console not valid')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('console')

        elif 'edit_console' in request.POST:
            editConsoleForm = EditConsoleForm(request.POST)

            if editConsoleForm.is_valid():
                editConsoleObject = self.model.objects.get(id=self.request.GET.get('console_name'))
                editConsoleObject.console_name = editConsoleForm.cleaned_data['console_name']
                editConsoleObject.pod_number = editConsoleForm.cleaned_data['pod_number']
                editConsoleObject.pod_location = editConsoleForm.cleaned_data['pod_location']
                editConsoleObject.console_ip_address = editConsoleForm.cleaned_data['console_ip_address']
                editConsoleObject.console_note = editConsoleForm.cleaned_data['console_note']

                editConsoleObject.save()

                messages.success(request, 'Successfully edited Console')
                print('Successfuly edited console')

            else:
                print('edit console not valid')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('console')

        return redirect('console')

@superuser_required()
class Scripts(LoginRequiredMixin, View):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        args = {}
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            template = loader.get_template('user/scripts.html')
            return TemplateResponse(request, template, args)

class Logout(View):
    def post(self, request):
        logout(request)
        return HttpResponseRedirect('/login')

