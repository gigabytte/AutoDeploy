from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.template import loader
from .forms import RegisterForm
from django.template.response import TemplateResponse

# this class is being deprecated in farvour of LDAP authication control
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

class Home(View):
    def get(self, request):
        Logout.checkLogin(request)
        return redirect('dashboard')

class Profile(View):
    def get(self, request):
        args = {}
        Logout.checkLogin(request)

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

class Dashboard(View):
    def get(self, request):
        Logout.checkLogin(request)

        template = loader.get_template('user/dashboard.html')
        return HttpResponse(template.render({}, request))

class Network(View):
    def get(self, request):
        Logout.checkLogin(request)

        template = loader.get_template('user/network.html')
        return HttpResponse(template.render({}, request))

class Windows(View):
    def get(self, request):
        args = {}
        Logout.checkLogin(request)

        template = loader.get_template('user/windows.html')
        return TemplateResponse(request, template, args)

class Devices(View):
    def get(self, request):
        args = {}
        Logout.checkLogin(request)

        template = loader.get_template('user/devices.html')
        return TemplateResponse(request, template, args)

class Scripts(View):
    def get(self, request):
        args = {}
        Logout.checkLogin(request)

        template = loader.get_template('user/scripts.html')
        return TemplateResponse(request, template, args)

class Logout(View):
    def checkLogin(request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
    def post(self, request):
        logout(request)
        return HttpResponseRedirect('/login')
