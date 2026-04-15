"""Crop app_icon.png to a circle and convert to ICO."""
from PIL import Image, ImageDraw

img = Image.open("app_icon.png").convert("RGBA")
w, h = img.size

# Find the dark circle — crop to square centered on the image
size = min(w, h)
left = (w - size) // 2
top = (h - size) // 2
img = img.crop((left, top, left + size, top + size))

# Create circular mask
mask = Image.new("L", (size, size), 0)
draw = ImageDraw.Draw(mask)
draw.ellipse([0, 0, size, size], fill=255)

# Apply mask — make corners transparent
img.putalpha(mask)

# Resize to 256x256
img = img.resize((256, 256), Image.LANCZOS)

# Save PNG
img.save("app_icon.png")

# Save ICO with multiple sizes
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
icons = [img.resize(s, Image.LANCZOS) for s in sizes]
icons[-1].save("app_icon.ico", format="ICO", sizes=sizes, append_images=icons[:-1])

print("Saved app_icon.png and app_icon.ico")
