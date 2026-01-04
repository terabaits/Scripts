import os
import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont

# === CONFIGURATION ===
csv_path = '/Users/king/Documents/GitHub/Scripts/QR generator/SHOP DATABASE - Lapa1.csv'
output_folder = '/Users/king/Documents/GitHub/Scripts/QR generator/Images'
logo_path = '/Users/king/Documents/GitHub/Scripts/QR generator/BLACK.png'
image_width = 600
image_height = 800
font_path = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'  # macOS built-in font

# === SETUP ===
os.makedirs(output_folder, exist_ok=True)
df = pd.read_csv(csv_path)

# Clean numeric columns with commas
df['Gala Cena(+21%)'] = df['Gala Cena(+21%)'].astype(str).str.replace(',', '.').astype(float)

# Load and resize logo
logo = Image.open(logo_path).convert("RGBA")
logo_size = 100  # Adjust this if logo appears too big or small
logo = logo.resize((logo_size, logo_size), Image.ANTIALIAS)

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
        error_correction=qrcode.constants.ERROR_CORRECT_H  # High error correction for logo
    )
    qr.add_data(link)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')

    # Embed logo in the center of the QR
    qr_width, qr_height = qr_img.size
    logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
    qr_img.paste(logo, logo_pos, mask=logo)

    # Create final image canvas
    img = Image.new('RGB', (image_width, image_height), color='white')
    draw = ImageDraw.Draw(img)

    # Load fonts
    try:
        title_font = ImageFont.truetype(font_path, size=40)
        price_font = ImageFont.truetype(font_path, size=36)
    except:
        title_font = ImageFont.load_default()
        price_font = ImageFont.load_default()

    # Draw Number
    draw.text((image_width // 2, 30), f"#{number}", font=title_font, fill="black", anchor="mm")

    # Paste QR Code in center
    qr_resized_size = 400
    qr_img = qr_img.resize((qr_resized_size, qr_resized_size), Image.ANTIALIAS)
    qr_x = (image_width - qr_resized_size) // 2
    qr_y = 150
    img.paste(qr_img, (qr_x, qr_y))

    # Draw Price
    draw.text((image_width // 2, qr_y + qr_resized_size + 50), f"Price: {price}", font=price_font, fill="black", anchor="mm")

    # Save image
    safe_title = f"{number} {title}".replace('/', '-').replace('\\', '-').strip()
    img.save(os.path.join(output_folder, f"{safe_title}.png"))

print("✅ QR code images with logo have been generated successfully!")
