from pathlib import Path

import cv2
import numpy as np


# ============================================================
# LumenRetinex - Retinex Image Enhancement
# ============================================================

SIGMA_SSR = 80
SIGMAS_MSR = (15, 80, 250)


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(input_path):
    """Load an image and validate it."""

    input_path = Path(input_path)

    image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(
            f"Could not load image: {input_path}"
        )

    if image.size == 0:
        raise ValueError("The input image is empty.")

    return image


# ============================================================
# NORMALIZATION
# ============================================================

def normalize_channel(
    channel,
    low_percentile=1,
    high_percentile=99
):
    """Normalize a floating-point channel to uint8."""

    channel = channel.astype(np.float32)

    low = float(np.percentile(channel, low_percentile))
    high = float(np.percentile(channel, high_percentile))

    if high - low < 1e-6:
        return np.clip(channel, 0, 255).astype(np.uint8)

    normalized = (channel - low) / (high - low)
    normalized = np.clip(normalized, 0.0, 1.0)

    return np.round(normalized * 255).astype(np.uint8)


# ============================================================
# IMAGE SAVING
# ============================================================

def save_image(output_path, image):
    """Create output directories and save an image."""

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = cv2.imwrite(str(output_path), image)

    if not success:
        raise ValueError(
            f"Could not save enhanced image: {output_path}"
        )


# ============================================================
# SINGLE-SCALE RETINEX (SSR)
# ============================================================

def single_scale_retinex(
    input_path,
    output_path,
    sigma=SIGMA_SSR
):
    """
    Single-Scale Retinex.

    R(x,y) = log(I(x,y) + epsilon)
             - log(G_sigma(x,y) + epsilon)

    Processing is performed on luminance to preserve color.
    """

    if sigma <= 0:
        raise ValueError("Sigma must be greater than zero.")

    image = load_image(input_path)

    # LAB separates brightness from color information.
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    luminance = lab[:, :, 0].astype(np.float32) + 1.0

    illumination = cv2.GaussianBlur(
        luminance,
        (0, 0),
        sigmaX=float(sigma),
        sigmaY=float(sigma)
    )

    illumination = np.maximum(illumination, 1.0)

    retinex = np.log(luminance) - np.log(illumination)

    # Normalize the Retinex response.
    retinex_normalized = normalize_channel(retinex)

    original_luminance = lab[:, :, 0].astype(np.float32)

    # Blend the result with original luminance.
    enhanced_luminance = (
        0.40 * original_luminance
        + 0.60 * retinex_normalized.astype(np.float32)
    )

    lab[:, :, 0] = np.clip(
        enhanced_luminance, 0, 255
    ).astype(np.uint8)

    enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    save_image(output_path, enhanced)

    return enhanced


# ============================================================
# MULTI-SCALE RETINEX (MSR)
# ============================================================

def multi_scale_retinex(
    input_path,
    output_path,
    sigmas=SIGMAS_MSR
):
    """
    Multi-Scale Retinex.

    Combines several Gaussian scales and processes luminance
    instead of independently stretching RGB color channels.
    This helps preserve more natural colors.
    """

    if not sigmas:
        raise ValueError("At least one Retinex scale is required.")

    if any(sigma <= 0 for sigma in sigmas):
        raise ValueError("All Retinex scales must be positive.")

    image = load_image(input_path)

    # Convert BGR to LAB.
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)

    original_luminance = lab[:, :, 0].astype(np.float32)

    # Avoid log(0).
    luminance = original_luminance + 1.0

    retinex = np.zeros_like(
        luminance, dtype=np.float32
    )

    # Compute Retinex at multiple scales.
    for sigma in sigmas:

        illumination = cv2.GaussianBlur(
            luminance,
            (0, 0),
            sigmaX=float(sigma),
            sigmaY=float(sigma)
        )

        illumination = np.maximum(
            illumination, 1.0
        )

        scale_response = (
            np.log(luminance)
            - np.log(illumination)
        )

        retinex += scale_response

    retinex /= len(sigmas)

    # Robust percentile normalization.
    low = float(np.percentile(retinex, 1))
    high = float(np.percentile(retinex, 99))

    if high - low < 1e-6:
        raise ValueError(
            "Insufficient luminance variation for Retinex."
        )

    normalized = np.clip(
        (retinex - low) / (high - low),
        0.0,
        1.0
    )

    retinex_luminance = normalized * 255.0

    # Blend with original luminance to reduce washed-out output.
    enhanced_luminance = (
        0.40 * original_luminance
        + 0.60 * retinex_luminance
    )

    lab[:, :, 0] = np.clip(
        enhanced_luminance, 0, 255
    ).astype(np.uint8)

    # Convert back to the original color space.
    enhanced = cv2.cvtColor(
        lab, cv2.COLOR_LAB2BGR
    )

    save_image(output_path, enhanced)

    return enhanced


# ============================================================
# IMAGE STATISTICS
# ============================================================

def image_statistics(image):
    """Return image dimensions, brightness and contrast."""

    gray = cv2.cvtColor(
        image, cv2.COLOR_BGR2GRAY
    )

    return {
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
        "brightness": round(
            float(np.mean(gray)), 2
        ),
        "contrast": round(
            float(np.std(gray)), 2
        )
    }


# ============================================================
# TEST BOTH ALGORITHMS
# ============================================================

def run_tests():

    base_dir = Path(__file__).resolve().parent.parent
    upload_dir = base_dir / "uploads"

    input_path = upload_dir / "dark.jpg"

    ssr_path = upload_dir / "retinex_enhanced.jpg"
    msr_path = upload_dir / "msr_enhanced.jpg"

    if not input_path.exists():
        raise FileNotFoundError(
            f"Image not found: {input_path}\n"
            "Place the original image at uploads/dark.jpg."
        )

    original = load_image(input_path)

    print("Original image statistics:")
    print(image_statistics(original))

    # Run SSR.
    ssr_result = single_scale_retinex(
        input_path, ssr_path
    )

    print("\nSingle-Scale Retinex completed.")
    print(f"Saved: {ssr_path}")
    print("Statistics:", image_statistics(ssr_result))

    # Run MSR.
    msr_result = multi_scale_retinex(
        input_path, msr_path
    )

    print("\nMulti-Scale Retinex completed.")
    print(f"Saved: {msr_path}")
    print("Statistics:", image_statistics(msr_result))

    print("\nAll Retinex tests completed successfully.")


if __name__ == "__main__":

    try:
        run_tests()

    except (
        ValueError,
        FileNotFoundError,
        cv2.error
    ) as error:
        print(f"\nEnhancement failed: {error}")