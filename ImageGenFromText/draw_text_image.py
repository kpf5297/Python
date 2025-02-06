from PIL import Image, ImageDraw, ImageFont

# Create a blank image with a light gray background
width, height = 800, 300
image = Image.new('RGB', (width, height), (240, 240, 240))
draw = ImageDraw.Draw(image)

# Load fonts (using default fonts for simplicity)
try:
    title_font = ImageFont.truetype("arial.ttf", 40)
    text_font = ImageFont.truetype("arial.ttf", 30)
except:
    title_font = ImageFont.load_default()
    text_font = ImageFont.load_default()

# Draw the circular portrait placeholder
draw.ellipse((50, 50, 150, 150), fill='gray')

# Add the curved name text
draw.text((30, 20), "Peter Drucker", fill="black", font=text_font)

# Add the quote text
quote_lines = [
    "Nothing is less productive",
    "than to make more efficient",
    "what should not be done at all."
]

y_position = 60
for i, line in enumerate(quote_lines):
    color = "green" if i == 2 else "black"
    draw.text((200, y_position + i*40), line, fill=color, font=text_font)

# Save the image
image.save("peter_drucker_quote.png")
