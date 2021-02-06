from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic, View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.template import loader


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

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