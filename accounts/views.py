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
            print(form.cleaned_data['password'])
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
            else:
                # Create the user:
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    'some@test.com',
                    form.cleaned_data['password']
                )
                #user.first_name = form.cleaned_data['first_name']
                #user.last_name = form.cleaned_data['last_name']
                #print(user.password)
                user.save()

                # redirect to login page:
                return HttpResponseRedirect('/login')


class Home(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            return redirect('dashboard')

def logout_view(request):
   logout(request)
   return HttpResponseRedirect('/login')

class Dashboard(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseRedirect('/login')
        else:
            template = loader.get_template('user/dashboard.html')
            return HttpResponse(template.render({}, request))