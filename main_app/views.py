from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Card, Photo
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

@login_required
def add_photo(request, card_id):
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            bucket = os.environ['S3_BUCKET']
            s3.upload_fileobj(photo_file, bucket, key)
            url = f"{os.environ['S3_BASE_URL']}{bucket}/{key}"
            Photo.objects.create(url=url, card_id=card_id)
        except Exception as e:
            print('An error occurred uploading file to S3')
            print(e)
    return redirect('detail', card_id=card_id)