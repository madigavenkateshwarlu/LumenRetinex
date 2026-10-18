import cv2
from pathlib import Path

# Project folder
BASE_DIR = Path(__file__).resolve().parent

# Input and output image paths
input_image = BASE_DIR / "uploads" / "dark.jpg"
output_image = BASE_DIR / "uploads" / "test_output.jpg"

# Read the image
img = cv2.imread(str(input_image))

if img is None:
    print("ERROR: Image could not be loaded.")
    print(f"Check that this file exists: {input_image}")
else:
    # Get image dimensions
    height, width, channels = img.shape

    print("Image loaded successfully!")
    print(f"Width: {width} pixels")
    print(f"Height: {height} pixels")
    print(f"Channels: {channels}")

    # Save a copy of the image
    success = cv2.imwrite(str(output_image), img)

    if success:
        print("\nSUCCESS: Image saved successfully!")
        print(f"Output file: {output_image}")
    else:
        print("\nERROR: Could not save the image.")