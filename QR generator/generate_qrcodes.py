import os
import math
import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageChops

# === CONFIGURATION ===
csv_path = '/Users/king/Documents/GitHub/Scripts/QR generator/SHOP DATABASE - Lapa1.csv'
output_folder = '/Users/king/Documents/GitHub/Scripts/QR generator/Images'
a4_output_folder = os.path.join(output_folder, 'A4_Pages')
logo_path = '/Users/king/Documents/GitHub/Scripts/QR generator/BLACK.png'
font_path = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'

image_width, image_height = 600, 600
a4_width, a4_height = 2480, 3508  # A4 at 300 DPI

# === SETUP ===
os.makedirs(output_folder, exist_ok=True)
os.makedirs(a4_output_folder, exist_ok=True)
df = pd.read_csv(csv_path)
df['Gala Cena(+21%)'] = df['Gala Cena(+21%)'].astype(str).str.replace(',', '.').astype(float)

# Load and resize logo
logo = Image.open(logo_path).convert("RGBA")
logo_size = 100
logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

# Fonts
try:
    title_font = ImageFont.truetype(font_path, size=34)
    price_font = ImageFont.truetype(font_path, size=30)
except:
    title_font = ImageFont.load_default()
    price_font = ImageFont.load_default()

# Helper: Crop whitespace from image
def crop_whitespace(image, background_color='white'):
    bg = Image.new(image.mode, image.size, background_color)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    return image.crop(bbox) if bbox else image

# Helper: Add border around image
def add_border(image, border=10, color='white'):
    w, h = image.size
    bordered = Image.new(image.mode, (w + 2*border, h + 2*border), color)
    bordered.paste(image, (border, border))
    return bordered

qr_images = []

# === MAIN LOOP ===
for index, row in df.iterrows():
    number = str(row['Nr'])
    title = str(row['Title'])
    price = f"{row['Gala Cena(+21%)']:.2f} €"
    link = str(row['Links'])

    if not link or link.lower() == 'nan':
        continue

    # Generate QR code
    qr = qrcode.QRCode(
        version=4,
        box_size=10,
        border=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )
    qr.add_data(link)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Embed logo
    qr_width, qr_height = qr_img.size
    logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    qr_img.paste(logo, logo_pos, mask=logo)

    # Resize QR
    qr_resized_size = 360
    qr_img = qr_img.resize((qr_resized_size, qr_resized_size), Image.Resampling.LANCZOS)

    # Create full image
    img = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(img)

    spacing_top = 20
    spacing_middle = 20
    spacing_bottom = 20

    number_text = f"#{number}"
    price_text = f"Price: {price}"

    number_text_height = draw.textbbox((0, 0), number_text, font=title_font)[3]
    price_text_height = draw.textbbox((0, 0), price_text, font=price_font)[3]

    content_height = spacing_top + number_text_height + spacing_middle + qr_resized_size + spacing_middle + price_text_height + spacing_bottom
    y_offset = (image_height - content_height) // 2

    draw.text((image_width // 2, y_offset), number_text, font=title_font, fill="black", anchor="ma")
    y_offset += number_text_height + spacing_middle
    img.paste(qr_img, ((image_width - qr_resized_size) // 2, y_offset))
    y_offset += qr_resized_size + spacing_middle
    draw.text((image_width // 2, y_offset), price_text, font=price_font, fill="black", anchor="ma")

    # Crop and border
    cropped = crop_whitespace(img)
    bordered = add_border(cropped, border=10)

    # Save
    safe_title = f"{number} {title}".replace('/', '-').replace('\\', '-').strip()
    bordered.save(os.path.join(output_folder, f"{safe_title}.png"))

    qr_images.append(bordered)

# === COMPILE A4 SHEETS ===
cols, rows = 4, 4
padding = 40
usable_width = a4_width - (cols + 1) * padding
usable_height = a4_height - (rows + 1) * padding
thumb_w = usable_width // cols
thumb_h = usable_height // rows
per_page = cols * rows
total_pages = math.ceil(len(qr_images) / per_page)

for page_num in range(total_pages):
    a4 = Image.new('RGB', (a4_width, a4_height), 'white')

    for i in range(per_page):
        img_index = page_num * per_page + i
        if img_index >= len(qr_images):
            break

        row = i // cols
        col = i % cols

        x = padding + col * (thumb_w + padding)
        y = padding + row * (thumb_h + padding)

        qr_img = qr_images[img_index]
        qr_w, qr_h = qr_img.size

        # Scale image to fit thumb_w x thumb_h (preserve aspect)
        scale_factor = min(thumb_w / qr_w, thumb_h / qr_h)
        new_w = int(qr_w * scale_factor)
        new_h = int(qr_h * scale_factor)
        resized = qr_img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        offset_x = x + (thumb_w - new_w) // 2
        offset_y = y + (thumb_h - new_h) // 2

        a4.paste(resized, (offset_x, offset_y))

    a4.save(os.path.join(a4_output_folder, f"A4_Page_{page_num + 1}.png"))

print("✅ All QR images cropped, bordered, and compiled into A4 pages!")
