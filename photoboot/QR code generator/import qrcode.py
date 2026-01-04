import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import inch
from reportlab.lib.colors import black
from PIL import Image
from datetime import datetime

def generate_qr(url):
    """Generate QR code PNG file named with today's date."""
    today = datetime.now().strftime("%Y-%m-%d")
    qr_filename = f"{today}.png"

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,  # minimal border for dense packing
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save(qr_filename)

    return qr_filename, today


def generate_pdf_with_copies(qr_image_path, date_str,
                             page_width=6 * inch, page_height=8 * inch,
                             rows=8, cols=6):
    """Create a PDF with 48 QR codes (8×6 grid) + trimming lines."""
    pdf_filename = f"{date_str}.pdf"
    c = canvas.Canvas(pdf_filename, pagesize=(page_width, page_height))

    usable_w = page_width
    usable_h = page_height

    qr_w = usable_w / cols
    qr_h = usable_h / rows
    qr_size = min(qr_w, qr_h)

    c.setLineWidth(0.25)  # thin trimming lines

    for r in range(rows):
        for col in range(cols):
            x = col * qr_size
            y = (rows - 1 - r) * qr_size

            # Draw QR
            c.drawImage(qr_image_path, x, y, width=qr_size, height=qr_size)

            # Draw trimming border
            c.setStrokeColor(black)
            c.rect(x, y, qr_size, qr_size, stroke=1, fill=0)

    c.save()
    print(f"Created PDF: {pdf_filename}")


if __name__ == "__main__":
    url = input("Enter URL for QR code: ")

    qr_file, date_str = generate_qr(url)
    generate_pdf_with_copies(qr_file, date_str)

    print("Done! 48-QR sheet (8×6 grid) and date-named files created successfully.")
