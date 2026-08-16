from PIL import Image

# Open the PNG
img = Image.open('assets/icon.png')

# Save as ICO
img.save('assets/icon.ico', format='ICO', sizes=[(256, 256)])

print("✅ Icon converted successfully!")