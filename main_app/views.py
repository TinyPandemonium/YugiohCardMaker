from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import uuid
import boto3
import os

from .models import Card

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

@login_required
def cards_index(request):
  cards = Card.objects.filter(user=request.user)
  return render(request, 'cards/index.html', {
    'cards': cards
  })

@login_required
def cards_detail(request, card_id):
  card = Card.objects.get(id=card_id)
  return render(request, 'cards/detail.html', { 'card': card })

class CardCreate(LoginRequiredMixin, CreateView):
  model = Card
  fields = ['name', 'attribute', 'description', 'star']
  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CardUpdate(LoginRequiredMixin, UpdateView):
  model = Card
  fields = ['name', 'attribute', 'description', 'star']

class CardDelete(LoginRequiredMixin, DeleteView):
  model = Card
  success_url = '/cards'

def signup(request):
  error_message = ''
  if request.method == 'POST':
    form = UserCreationForm(request.POST)
    if form.is_valid():
      user = form.save()
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)