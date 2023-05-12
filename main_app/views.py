from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Card, Photo
from PIL import Image, ImageDraw
from io import BytesIO
import psycopg2
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

class myTemplate():
    def __init__(self, name, description, image, user):
        self.name = name
        self.description = description
        self.image = image
        self.user = user
        print('hello init')
    print('hello')    
    
    def draw(self):
        template_folder = 'main_app/card_template'
        template_filename = 'base.png'
        template_path = os.path.join(template_folder, template_filename)
        print(template_path)
        img = Image.open(template_path, 'r').convert('RGB')  # Opens Template Image

        if self.image:
            # Open and resize the uploaded image
            uploaded_img = Image.open(self.image).convert("RGBA")
            uploaded_img = uploaded_img.resize((278, int(uploaded_img.size[1] * (278 / uploaded_img.size[0]))))

            # Calculate the position to paste the uploaded image
            paste_x = 31
            paste_y = 141

            # Calculate the maximum width and height for the uploaded image to fit inside the base image
            max_width = 278
            max_height = 322

            # Adjust the position and size of the uploaded image if it exceeds the maximum width or height
            if uploaded_img.width > max_width:
                uploaded_img = uploaded_img.resize((max_width, int(uploaded_img.height * (max_width / uploaded_img.width))))
            if uploaded_img.height > max_height:
                uploaded_img = uploaded_img.resize((int(uploaded_img.width * (max_height / uploaded_img.height)), max_height))

            # Calculate the position to center the uploaded image within the defined area in the base image
            paste_x += (max_width - uploaded_img.width) // 2
            paste_y += (max_height - uploaded_img.height) // 2

            # Paste the uploaded image into the base image
            img.paste(uploaded_img, (paste_x, paste_y), mask=uploaded_img)
        
        imgdraw = ImageDraw.Draw(img)  # Create a canvas
        imgdraw.text((515, 152), self.name, (0, 0, 0))  # Draws name
        imgdraw.text((654, 231), self.description, (0, 0, 0))  # Draws description

        image_bytes = BytesIO()
        img.save(image_bytes, format='PNG')
        image_bytes.seek(0)

        conn = psycopg2.connect(
            database="TinyPandemonium/yugiohcardmaker",
            user="TinyPandemonium",
            password=os.environ['DB_PASSWORD'],
            host="db.bit.io",
            port="5432"
        )

        cursor = conn.cursor()

        cursor.execute("INSERT INTO card (user_id, name, description, image) VALUES (%s, %s, %s, %s)",
                       (self.user.id, self.name, self.description, psycopg2.Binary(image_bytes.read())))

        # Commit the transaction
        conn.commit()

        # Close the cursor and the database connection
        cursor.close()
        conn.close()


class CardCreate(LoginRequiredMixin, CreateView):
    model = Card
    fields = ['name', 'attribute', 'description', 'star']

    def form_valid(self, form):
        form.instance.user = self.request.user
        template = myTemplate(
            name=form.cleaned_data['name'],
            description=form.cleaned_data['description'],
            image=form.cleaned_data.get('image', None),
            user=self.request.user
        )
        template.draw()
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


@login_required
def generate_card(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        template = myTemplate(name, description, image, request)
        template.draw()

        return redirect('cards')  # Redirect to the cards view after generating the card

    return render(request, 'generate_card.html')