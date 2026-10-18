import cv2
import numpy as np
from pathlib import Path


def logarithmic_enhancement(input_path, output_path):
    # Read the input image
    image = cv2.imread(str(input_path))

    if image is None:
        raise ValueError(f"Cannot read image: {input_path}")

    # Convert pixel values to floating-point numbers
    image_float = image.astype(np.float32)

    # Apply logarithmic transformation: s = c * log(1 + r)
    c = 255.0 / np.log1p(255.0)
    enhanced = c * np.log1p(image_float)

    # Convert pixel values back to the 0-255 range
    enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)

    # Save enhanced image
    success = cv2.imwrite(str(output_path), enhanced)

    if not success:
        raise ValueError(f"Could not save image: {output_path}")

    return enhanced


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent

    input_path = base_dir / "uploads" / "dark.jpg"
    output_path = base_dir / "uploads" / "log_enhanced.jpg"

    try:
        result = logarithmic_enhancement(input_path, output_path)

        print("Logarithmic enhancement completed!")
        print(f"Image dimensions: {result.shape[1]} x {result.shape[0]}")
        print(f"Enhanced image saved to: {output_path}")

    except (ValueError, cv2.error) as error:
        print(f"Enhancement failed: {error}")