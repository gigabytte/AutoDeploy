from accounts.models import Console, Device, Scripts
from django.shortcuts import render, redirect
from django.views import generic, View
from django.views.generic import TemplateView
from django.contrib.auth import logout, login
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.template import loader
from .forms import *
from django.template.response import TemplateResponse
from django_auth_ldap.backend import LDAPBackend
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Super Class used to eval user creds against admin access
class AdminStaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):

    def test_func(self):
        return self.request.user.is_superuser


# this class is being deprecated in farvour of LDAP authication 
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

# Class returns login form or dashboard based on root navigation
class Home(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            return redirect('dashboard')

# Class returns profile.html along with profile info on user
class Profile(LoginRequiredMixin, View):

    login_url = '/profile/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        args = {}

        userEmail = request.user.email
        userFirstName = request.user.first_name
        userLastName = request.user.last_name
        args['user_firstname'] = userFirstName
        # check if firstname is set for user if not use username to prevent none error
        if not userFirstName:
            args['user_firstname'] = request.user.username
        args['user_lastname'] = userLastName
        args['user_email'] = userEmail
        template = loader.get_template('user/profile.html')
        return TemplateResponse(request, template, args)

# class returns basic dashbaord section
# future content might include search functionlity and live device stats
class Dashboard(LoginRequiredMixin, View):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):

        template = loader.get_template('user/dashboard.html')
        return HttpResponse(template.render({}, request))

# class returns script deploy page for console and network equipment
class Network(LoginRequiredMixin, TemplateView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/network.html'
    model = Console

    def get_context_data(self, **kwargs):
        # return script and console models for script selection
        context = super(Network, self).get_context_data(**kwargs)
        context['script_details'] = Scripts.objects.filter(device_type='0')
        context['console_details'] = self.model.objects.all()

        if 'select_console' not in kwargs:
            kwargs['select_console'] = SelectConsoleForm()
        if 'select_script' not in kwargs:
            kwargs['select_script'] = SelectScriptForm()

        return context

    # on post start ansible function using comand line arugments. 
    # provide command line arguments based on user selection
    # console output should be fed back to use in async fashion as scripts finish / fail
    # post function is delivered by ajax requedt to provide async functionality back to user without full reload
    def post(self, request, *args, **kwargs):
        ctxt = {}
        if request.POST.get('action') == 'deploy_script':
            consoleID = request.POST.get('console_id')
            scriptID = request.POST.get('script_id')
            # some ansible cmd line class calling would go here
            # should report in async fashion to update view with logging info from Ansible
            print(consoleID, scriptID)

        return redirect('network')


class Windows(LoginRequiredMixin, TemplateView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/windows.html'
    model = Device

    def get_context_data(self, **kwargs):
        # return script and device models for script selection
        context = super(Windows, self).get_context_data(**kwargs)
        context['script_details'] = Scripts.objects.filter(device_type='1')
        context['device_details'] = self.model.objects.all()

        if 'select_console' not in kwargs:
            kwargs['select_console'] = SelectConsoleForm()
        if 'select_script' not in kwargs:
            kwargs['select_script'] = SelectScriptForm()

        return context

    # on post start ansible function using comand line arugments. 
    # provide command line arguments based on user selection
    # console output should be fed back to use in async fashion as scripts finish / fail
    # post function is delivered by ajax requedt to provide async functionality back to user without full reload
    def post(self, request, *args, **kwargs):
        ctxt = {}
        if request.POST.get('action') == 'deploy_script':
            deviceID = request.POST.get('device_id')
            scriptID = request.POST.get('script_id')

            # some ansible cmd line class calling would go here
            # should report in async fashion to update view with logging info from Ansible

            print(deviceID, scriptID)

        return redirect('windows')

# class returns all devices store in DB as dump
class All_Devices(AdminStaffRequiredMixin, TemplateView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/all_devices.html'
    model = Console

    def get_context_data(self, **kwargs):
        # gather console and windows devices and pass to view using kwargs
        context = super(All_Devices, self).get_context_data(**kwargs)
        context['device_details'] = Device.objects.all()
        context['console_details'] = self.model.objects.all()

        return context

# class allows for the creation, deletion and editing of Windows devices
class Equipment(AdminStaffRequiredMixin, generic.ListView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/equipment.html'
    model = Device
    
    def get_queryset(self):
        # return Device details based on user GET selection from drop down
        if self.request.GET.get('device_name'):
            self.selectedDeviceDetails = self.model.objects.get(pk=self.request.GET.get('device_name'))
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        # pass all models to view as kwargs
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
        # based on form id triggered by user POST request perform method
        # this functionality is needed to support mutiple POST forms in one view
        if 'add_device' in request.POST:
            addDeviceForm = AddDeviceForm(request.POST)
            if addDeviceForm.is_valid():

                podNumberSelected = addDeviceForm.cleaned_data['pod_number']
                podLocationSelected = addDeviceForm.cleaned_data['pod_location']
                deviceIPAdressAdded = addDeviceForm.cleaned_data['device_ip_address']
                deviceMACAdressAdded = addDeviceForm.cleaned_data['device_mac_address']
                read_podLocationSelected = 'Networking Lab' if podLocationSelected == 0 else 'Datacenter'
   
                # check if 2 devices are already added to the same pod and located in the same pod location
                # should only be 2 devices per pod
                if  len(self.model.objects.filter(pod_number=podNumberSelected).filter(pod_location=podLocationSelected)) < 2:
                    # check if duplicate ip address exsists with another PC
                    if not self.model.objects.filter(device_ip_address=deviceIPAdressAdded).filter(pod_location=podLocationSelected):
                        # check if duplicate MAC address exsists with another PC
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
                    messages.info(request, 'There are 2 Devices already asscoaited with Pod Number %s Located in %s, please try again or delete old Device first.' % (podNumberSelected, read_podLocationSelected))
            else:
                print('invalid Device form')
                print(addDeviceForm.errors)
                # if user fails to fill out form correctly send message error to view
                messages.error(request, 'Form Error please Try Again!')
                return redirect('equipment')

        elif 'delete_device' in request.POST:
            deleteDeviceForm = DeleteDeviceForm(request.POST)

            if deleteDeviceForm.is_valid():
                # gather device ID from device_name form field
                deviceID = deleteDeviceForm.cleaned_data['device_name']
                # delete device based on ID from DB
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
                # save model object based on user drop down menu GET request.
                # all values in form are saved based on whats populated
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

# class used to create, delete and edit Console objects based on the Console model
class Console(AdminStaffRequiredMixin, generic.ListView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/console.html'
    model = Console
    
    def get_queryset(self):
        # cutom query based on user dropdown GET request selection, similar to equipment class functionality
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
        # based on form id triggered by user POST request perform method
        # this functionality is needed to support mutiple POST forms in one view
        if 'add_console' in request.POST:
            addConsoleForm = AddConsoleForm(request.POST)
            if addConsoleForm.is_valid():

                podNumberSelected = addConsoleForm.cleaned_data['pod_number']
                podLocationSelected = addConsoleForm.cleaned_data['pod_location']
                consoleIPAdressAdded = addConsoleForm.cleaned_data['console_ip_address']
                read_podLocationSelected = 'Networking Lab' if podLocationSelected == 0 else 'Datacenter'
                # Check if console is assocated with pod number and pod location first before adding
                # ** NOTE ** some consoles in datacenter have odd associations may need to change in future
                if not self.model.objects.filter(pod_number=podNumberSelected).filter(pod_location=podLocationSelected):
                    # check if console with duplicate IP exists
                    if not self.model.objects.filter(console_ip_address=consoleIPAdressAdded).filter(pod_location=podLocationSelected):
                        # save Console to DB
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
                # gather console ID from console_name form field
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
                # save model object based on user drop down menu GET request.
                # all values in form are saved based on whats populated
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

# class Dumps all script stored in DB 
class All_Scripts(AdminStaffRequiredMixin, generic.ListView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/all_scripts.html'
    model = Scripts
    
    def get_queryset(self):
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs

# class adds scripts to db
class Add_Scripts(AdminStaffRequiredMixin, View):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    def get(self, request):
        args = {}
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            template = loader.get_template('user/add_scripts.html')
            return TemplateResponse(request, template, args)

    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'add_scripts' in request.POST:
            
            addScriptsForm = AddScriptsForm(request.POST, request.FILES or None)
            if addScriptsForm.is_valid():
                # check if script uploaded
                if len(request.FILES) != 0:
                    # get first file in file list, cant upload mutiple scripts at once
                    fileList = request.FILES.getlist('script_file')[0]

                    # gather some facts based on script uploaded 
                    addScriptsForm.script_ext = fileList.content_type
                    addScriptsForm.script_size = fileList.size
                    # save script to db, on save function scripts are aded to the /media dir
                    # save functionality for scripts is stored in model view
                    addScriptsForm.save()
                    messages.success(request, 'Added New Script Scuccessfully!')
                else:
                    messages.error(request, 'File MISSING, please upload Script file')
                
                return redirect('add_scripts')
            else:
                print('invalid console form')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('add_scripts')

        return redirect('add_scripts')

# class edits scripts in db
class Edit_Scripts(AdminStaffRequiredMixin, generic.ListView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/edit_scripts.html'
    model = Scripts
    
    def get_queryset(self):
        # cutom query based on user dropdown GET request selection, similar to equipment class functionality
        if self.request.GET.get('script_name'):
            self.selectedScriptDetails = self.model.objects.get(pk=self.request.GET.get('script_name'))
        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)

        if self.request.GET.get('script_name'):
            kwargs['script_details'] = self.selectedScriptDetails

        return kwargs

    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'edit_script' in request.POST:
            # get script object from database that is selected by user
            editScriptFormObject = self.model.objects.get(id=self.request.GET.get('script_name'))
            editScriptForm = EditScriptsForm(request.POST, instance=editScriptFormObject)
            if editScriptForm.is_valid():
                # save model object based on user drop down menu GET request.
                # all values in form are saved based on whats populated
                editScriptFormObject.script_name = editScriptForm.cleaned_data['script_name']
                editScriptFormObject.script_version = editScriptForm.cleaned_data['script_version']
                editScriptFormObject.device_type = editScriptForm.cleaned_data['device_type']
                editScriptFormObject.is_staff = editScriptForm.cleaned_data['is_staff']
                editScriptFormObject.script_note = editScriptForm.cleaned_data['script_note']

                # ** NOTE ** Currently cannot replace script with new script upload
                # script update file method in Scripts model not implemented
                editScriptFormObject.update_save()

                messages.success(request, 'Successfully edited Script')
                print('Successfuly edited script')

            else:
                print('edit script not valid')
                print(editScriptForm.errors)
                messages.error(request, 'Form Error please Try Again!')
                return redirect('edit_scripts')
            
        return redirect('edit_scripts')


# class deletes script objects from DB
class Delete_Scripts(AdminStaffRequiredMixin, generic.ListView):

    login_url = '/login/'
    redirect_field_name = 'redirect_to'

    template_name = 'user/delete_scripts.html'
    model = Scripts
    
    def get_queryset(self):

        return self.model.objects.all()

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        return kwargs

    def post(self, request, *args, **kwargs):
        ctxt = {}
        
        if 'delete_scripts' in request.POST:

            deleteScriptsForm = DeleteScriptsForm(request.POST)
            if deleteScriptsForm.is_valid():
                # get script ID from user drop down form selection
                scriptID = deleteScriptsForm.cleaned_data['script_name']
                # filter for object by ID and delete
                self.model.objects.filter(id=scriptID).delete()

                messages.success(request, 'Successfully deleted Script')
                print('Successfuly delete script')

            else:
                print('delete script not valid')
                messages.error(request, 'Form Error please Try Again!')
                return redirect('delete_scripts')

        return redirect('delete_scripts')

# class logs user out of app killing session token
class Logout(View):
    def post(self, request):
        logout(request)
        return HttpResponseRedirect('/login')

