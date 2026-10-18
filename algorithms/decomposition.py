import cv2
import numpy as np
from pathlib import Path


def illumination_reflectance_decomposition(
    input_path,
    output_dir,
    sigma=80,
    enhancement_strength=1.5
):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read image
    image = cv2.imread(str(input_path))

    if image is None:
        raise ValueError(f"Cannot read image: {input_path}")

    # Convert to float in range 0-1
    image_float = image.astype(np.float32) / 255.0

    # Estimate illumination from grayscale image
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_float = gray.astype(np.float32) / 255.0

    illumination = cv2.GaussianBlur(
        gray_float,
        (0, 0),
        sigmaX=sigma,
        sigmaY=sigma
    )

    # Avoid division by zero
    illumination = np.maximum(illumination, 0.05)

    # Reflectance estimate: I = R * L, so R = I / L
    reflectance = image_float / illumination[:, :, np.newaxis]
    reflectance = np.clip(reflectance, 0.0, 1.0)

    # Brighten illumination while retaining its spatial variation
    enhanced_illumination = np.power(
        illumination,
        1.0 / enhancement_strength
    )

    # Reconstruct enhanced image
    enhanced = reflectance * enhanced_illumination[:, :, np.newaxis]
    enhanced = np.clip(enhanced, 0.0, 1.0)

    # Convert outputs to 8-bit images
    illumination_img = np.clip(
        illumination * 255, 0, 255
    ).astype(np.uint8)

    reflectance_img = np.clip(
        reflectance * 255, 0, 255
    ).astype(np.uint8)

    enhanced_img = np.clip(
        enhanced * 255, 0, 255
    ).astype(np.uint8)

    # Save intermediate and final results
    outputs = {
        "illumination.png": illumination_img,
        "reflectance.png": reflectance_img,
        "decomposition_enhanced.jpg": enhanced_img
    }

    for filename, output in outputs.items():
        output_path = output_dir / filename

        if not cv2.imwrite(str(output_path), output):
            raise ValueError(f"Could not save: {output_path}")

        print(f"Saved: {output_path}")

    return illumination_img, reflectance_img, enhanced_img


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent.parent
    input_path = base_dir / "uploads" / "dark.jpg"
    output_dir = base_dir / "uploads"

    try:
        _, _, result = illumination_reflectance_decomposition(
            input_path,
            output_dir
        )

        print("\nIllumination-Reflectance decomposition completed!")
        print(f"Image dimensions: {result.shape[1]} x {result.shape[0]}")

    except (ValueError, cv2.error) as error:
        print(f"Decomposition failed: {error}")