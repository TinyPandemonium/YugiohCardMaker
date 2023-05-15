<div align="center"> 

# Welcome To Yugioh Card Maker

## Built And Maintained By **[Roger Gonzalez](https://www.linkedin.com/in/rogerdoublez/)**

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
![Maintainer](https://img.shields.io/badge/Maintainer-RogerGonzalez-blue)
![Ask](https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg)

### With Help From These Programs

![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![CSS](https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E)
![Git](https://img.shields.io/badge/GIT-E44C30?style=for-the-badge&logo=git&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)

![Visual Studio Code](https://img.shields.io/badge/Visual_Studio_Code-0078D4?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)
![Heroku badge](https://img.shields.io/badge/Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%23563D7C.svg?style=for-the-badge&logo=bootstrap&logoColor=white)![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white)


### [click here to launch the site](https://yugiohcardmaker.herokuapp.com/)


## What Is Yugioh Card Maker?

It's a simple app where you upload an image from your computer, give it a name, description, amongst many other things, and it generates a Yugioh card for you in a nice and neat format.

## Getting Started
Either log in if you're a returning user, or sign up for an account using the separate tabs in the navbar. Once you're successfully logged in you can start adding cards or check out previous cards you've created. You can also go back and edit or delete the cards if you're ashamed of what you've done.

</div>

## Preview Of The Site
<details><summary>a few screenshots of the site</summary>

![](https://imgur.com/GIv8Pia.png)
![](https://imgur.com/jLB7Tvr.png)
![](https://imgur.com/iB52r3b.png)

</details>

## Issues Encountered 
for the longest time I couldn't get this piece of code to work

<details><summary>code</summary>

```python
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

        except MutableMapping as e:
          print('An error occurred uploading file to S3')
          print(e)
          traceback.print_exc()
    return redirect('detail', card_id=card_id)
```

</details>

and it bottlenecked my whole process. little did I know it would be the least of my problems. I had to reformat it from what it was originally because I was making one too many GET and SAVE requests.

## Proudest Piece Of Code

<details><summary>code</summary>

```python
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
```

this piece of code is doing a lot of the heavy lifting once a user uploads a photo and inputs the card info.

</details>


## Future Plans

- Get the deployed site properly working
- Implement different types of card templates such as Fusion, Spell, Etc.
- Better responsive design

## Special Shoutouts 

### The Instructors Over At GA: 
- **[Kenneth Chang](https://www.linkedin.com/in/kenneth-chang-94569a142/)** (SEI Lead Instructor)
- **[Matthew Gonczar](https://www.linkedin.com/in/matthew-gonczar/)** (Senior Instructional Associate)
- **[Evan Maloney](https://www.linkedin.com/in/evanpmaloney/)** (Instructional Associate)
- **[Payne Fulcher](https://www.linkedin.com/in/payne-fulcher/)** (Instructional Associate)
- **[Megan Hawkins](https://www.linkedin.com/in/mhawkins28/)** (Instructional Associate)

### Fellows At GA

- **[Ryan Le](https://www.linkedin.com/in/ryanqle/)**
- **[Sally Kam](https://www.linkedin.com/in/sallykam/)**
- **[Eric Hung](https://www.linkedin.com/in/erichungdev/)**
- **[Yuta Okkotsu](https://www.linkedin.com/in/yutaokkotsu/)**
- **[Kolbi Ivey](https://www.linkedin.com/in/kolbi-ivey-15b5631a8/)**
**[]()**