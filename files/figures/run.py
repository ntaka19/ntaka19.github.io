from PIL import Image

image="profile.png"
dest="profile2.png"

img = Image.open(image)
img.putalpha(200)  # Half alpha; alpha argument must be an int
img.save(dest)
