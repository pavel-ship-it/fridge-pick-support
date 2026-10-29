"""One-off: build optimised web images from the store assets into site/assets/img."""
from PIL import Image
import os
S = '/workspace/fridge-pick-store'
OUT = os.path.join(os.path.dirname(__file__), 'assets', 'img')
os.makedirs(OUT, exist_ok=True)
shots = ['01_home', '02_recipe', '03_im_hungry', '04_suggestions', '05_week_plan', '06_shopping_list', '07_my_fridge']
for n in shots:
    im = Image.open(f'{S}/screenshots/android-phone/{n}.png').convert('RGB')
    for w in (360, 720):
        im.resize((w, w * 2), Image.LANCZOS).save(f'{OUT}/{n}-{w}.webp', 'WEBP', quality=78, method=6)
card = Image.open('/workspace/fridge-pick-share-samples/omelette.png').convert('RGB')
for w in (360, 720):
    h = round(card.height * w / card.width)
    card.resize((w, h), Image.LANCZOS).save(f'{OUT}/share_card-{w}.webp', 'WEBP', quality=80, method=6)
print('card', card.size)
icon = Image.open(f'{S}/icon/icon_1024.png').convert('RGB')
icon.resize((192, 192), Image.LANCZOS).save(f'{OUT}/icon-192.webp', 'WEBP', quality=85)
icon.resize((512, 512), Image.LANCZOS).save(f'{OUT}/icon-512.jpg', 'JPEG', quality=88)
icon.resize((180, 180), Image.LANCZOS).save(f'{OUT}/../../apple-touch-icon.png', optimize=True)
icon.resize((32, 32), Image.LANCZOS).save(f'{OUT}/../../favicon.png', optimize=True)
icon.resize((48, 48), Image.LANCZOS).save(f'{OUT}/../../favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
for lang in ('en', 'ru'):
    Image.open(f'{S}/play/feature_graphic_{lang}.png').convert('RGB').save(f'{OUT}/og-{lang}.jpg', 'JPEG', quality=85, optimize=True, progressive=True)
