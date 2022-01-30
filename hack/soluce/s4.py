import random
from PIL import Image

flag = "FLAG{tout-rouge}"

img = Image.new('RGB', (128, len(flag)))
for y, c in enumerate(flag):
    for x in range(ord(c)):
        img.putpixel((x,y), (255, int(random.random() * 255), int(random.random() * 255)))
img.save('s4.png')


img = Image.open('s4.png')
px = img.load()
w,h = img.size
for y in range(h):
    s = 0
    for x in range(w):
        pixel = img.getpixel((x,y))
        if pixel[0] == 255:
            s += 1
    print(chr(s), end='')
