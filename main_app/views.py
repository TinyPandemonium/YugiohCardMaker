from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Card, Photo
from PIL import Image, ImageDraw, ImageFont
from collections.abc import MutableMapping
from io import BytesIO
import uuid
import boto3
import os
import tempfile
import shutil
import textwrap
import traceback
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
  fields = ['name', 'attribute', 'description', 'star', 'attack', 'defense']
  def form_valid(self, form):
    form.instance.user = self.request.user
    return super().form_valid(form)

class CardUpdate(LoginRequiredMixin, UpdateView):
  model = Card
  fields = ['name', 'attribute', 'description', 'star', 'attack', 'defense']

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

class ImageManipulator:
    @staticmethod
    def manipulate_image(card):
        background_image = Image.open('static/card_template/base.png')
        draw = ImageDraw.Draw(background_image)

        # Set the coordinates for each attribute
        name_coords = (30, 40)
        description_coords = (30, 460)
        attack_coords = (270, 558)
        defense_coords = (355, 558)

        # Wrap the text if it exceeds the maximum width
        wrapped_name = textwrap.fill(card.name, width=70)
        wrapped_description = textwrap.fill(card.description, width=85)

        # Define minimum and maximum font sizes
        min_font_size = 7
        min_name_font = 13
        max_font_size = 30
        max_name_font = 40

        # Calculate font sizes based on text lengths
        name_font_size = max(min_name_font, min(max_name_font, 30 - len(card.name)))
        description_font_size = max(min_font_size, min(max_font_size, 50 - len(card.description)))
        attack_font_size = 14
        defense_font_size = 14

        font_path = 'static/card_template/text.ttf'
        name_font = ImageFont.truetype(font_path, size=name_font_size)
        description_font = ImageFont.truetype(font_path, size=description_font_size)
        attack_font = ImageFont.truetype(font_path, size=attack_font_size)
        defense_font = ImageFont.truetype(font_path, size=defense_font_size)

        # Write each attribute to the image with their respective coordinates and font
        draw.text(name_coords, wrapped_name, fill=(0, 0, 0), font=name_font)
        draw.text(description_coords, wrapped_description, fill=(0, 0, 0), font=description_font)
        draw.text(attack_coords, f"{card.attack}", fill=(0, 0, 0), font=attack_font)
        draw.text(defense_coords, f"{card.defense}", fill=(0, 0, 0), font=defense_font)

        # Load the star image
        star_image = Image.open('static/card_template/star.png')

        # Calculate the number of star images to be placed
        num_stars = min(card.star, 12)

        # Set the initial position for the star images
        star_x = 350
        star_y = 80

        # Multiply the star image based on the card's star field
        for _ in range(num_stars):
            background_image.paste(star_image, (star_x, star_y), mask=star_image)
            star_x -= star_image.width
        # Load the attribute image based on the selected attribute
        attribute_image_path = f"static/card_template/{card.attribute.lower()}.png"
        attribute_image = Image.open(attribute_image_path)

        # Paste the attribute image onto the background image
        attribute_width = 30
        attribute_height = 30
        attribute_image = attribute_image.resize((attribute_width, attribute_height))
        attribute_x = 360
        attribute_y = 34
        background_image.paste(attribute_image, (attribute_x, attribute_y), mask=attribute_image)

        return background_image
        

@login_required
def add_photo(request, card_id):
    photo_file = request.FILES.get('photo-file', None)
    if photo_file:
        Photo.objects.filter(card_id=card_id).delete()
        s3 = boto3.client('s3')
        key = uuid.uuid4().hex[:6] + photo_file.name[photo_file.name.rfind('.'):]
        try:
            bucket = os.environ['S3_BUCKET']

            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()

            # Save the file temporarily in the directory
            file_path = os.path.join(temp_dir, key)
            with open(file_path, 'wb') as f:
                for chunk in photo_file.chunks():
                    f.write(chunk)

            # Open the file using PIL
            uploaded_image = Image.open(file_path)

            # Perform the image manipulation
            desired_width = 320
            desired_height = 322
            uploaded_image = uploaded_image.resize((desired_width, desired_height))
            card = Card.objects.get(id=card_id)
            background_image = ImageManipulator.manipulate_image(card)
            background_image.paste(uploaded_image, (51, 111))

            # Save the modified image to a buffer
            image_buffer = BytesIO()
            background_image.save(image_buffer, format='PNG')
            image_buffer.seek(0)

            # Upload the modified image to S3
            modified_key = f"modified/{key}"
            s3.upload_fileobj(image_buffer, bucket, modified_key)
            modified_url = f"{os.environ['S3_BASE_URL']}{bucket}/{modified_key}"

            # Create the Photo object
            Photo.objects.create(url=modified_url, card_id=card_id)

            # Delete the temporary directory and its contents
            shutil.rmtree(temp_dir)

        except Exception as e:
          print('An error occurred uploading file to S3')
          print(e)
          traceback.print_exc()
    return redirect('detail', card_id=card_id)