from pathlib import Path

import cv2
import numpy as np


# ============================================================
# LumenRetinex - Retinex Image Enhancement
# ============================================================

SIGMA_SSR = 80
SIGMAS_MSR = (15, 80, 250)

# Preserve the original luminance to reduce washed-out output.
ORIGINAL_WEIGHT = 0.40
RETINEX_WEIGHT = 0.60

EPSILON = 1.0


# ============================================================
# IMAGE LOADING
# ============================================================

def load_image(input_path):
    """Load and validate a colour image."""
    input_path = Path(input_path)

    image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)

    if image is None:
        raise ValueError(f"Could not load image: {input_path}")

    if image.size == 0:
        raise ValueError("The input image is empty.")

    return image


# ============================================================
# NORMALIZATION
# ============================================================

def percentile_normalize(image, low_percentile=1, high_percentile=99):
    """Normalize image values robustly using percentiles."""
    image = image.astype(np.float32)

    low = float(np.percentile(image, low_percentile))
    high = float(np.percentile(image, high_percentile))

    if high - low < 1e-6:
        return np.zeros_like(image, dtype=np.float32)

    normalized = (image - low) / (high - low)

    return np.clip(normalized, 0.0, 1.0)


# ============================================================
# GAUSSIAN ILLUMINATION ESTIMATION
# ============================================================

def estimate_illumination(luminance, sigma):
    """
    Estimate illumination using Gaussian blur.

    For large Gaussian scales, blur a reduced-resolution image
    and resize it back. This reduces the cost of large-scale
    illumination estimation.

    The reduction is an approximation, so the output should
    be checked visually against the full-resolution version.
    """
    luminance = luminance.astype(np.float32)

    if sigma >= 200:
        factor = 4
    elif sigma >= 80:
        factor = 2
    else:
        factor = 1

    height, width = luminance.shape[:2]

    if factor == 1:
        illumination = cv2.GaussianBlur(
            luminance,
            (0, 0),
            sigmaX=float(sigma),
            sigmaY=float(sigma),
            borderType=cv2.BORDER_REFLECT
        )
    else:
        small_width = max(1, width // factor)
        small_height = max(1, height // factor)

        small_luminance = cv2.resize(
            luminance,
            (small_width, small_height),
            interpolation=cv2.INTER_AREA
        )

        small_illumination = cv2.GaussianBlur(
            small_luminance,
            (0, 0),
            sigmaX=float(sigma) / factor,
            sigmaY=float(sigma) / factor,
            borderType=cv2.BORDER_REFLECT
        )

        illumination = cv2.resize(
            small_illumination,
            (width, height),
            interpolation=cv2.INTER_LINEAR
        )

    # Prevent log(0).
    return np.maximum(illumination, EPSILON)


# ============================================================
# RETINEX RECONSTRUCTION
# ============================================================

def reconstruct_from_luminance(lab, enhanced_luminance):
    """Replace LAB luminance while retaining original colour channels."""
    output_lab = lab.copy()

    output_lab[:, :, 0] = np.clip(
        enhanced_luminance, 0, 255
    ).astype(np.uint8)

    return cv2.cvtColor(output_lab, cv2.COLOR_LAB2BGR)


# ============================================================
# SINGLE-SCALE RETINEX (SSR)
# ============================================================

def single_scale_retinex(input_path, output_path=None, sigma=SIGMA_SSR):
    """
    Apply Single-Scale Retinex to the LAB luminance channel.

    Parameters:
        input_path: Input image path.
        output_path: Optional output image path.
        sigma: Gaussian scale.

    Returns:
        Enhanced BGR image as a NumPy array.
    """
    if sigma <= 0:
        raise ValueError("SSR sigma must be positive.")

    image = load_image(input_path)

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    original_luminance = lab[:, :, 0].astype(np.float32)

    luminance = original_luminance + EPSILON

    illumination = estimate_illumination(luminance, sigma)

    response = np.log(luminance) - np.log(illumination)

    normalized = percentile_normalize(response)
    retinex_luminance = normalized * 255.0

    enhanced_luminance = (
        ORIGINAL_WEIGHT * original_luminance
        + RETINEX_WEIGHT * retinex_luminance
    )

    enhanced = reconstruct_from_luminance(
        lab, enhanced_luminance
    )

    if output_path is not None:
        save_image(enhanced, output_path)

    return enhanced


# ============================================================
# MULTI-SCALE RETINEX (MSR)
# ============================================================

def multi_scale_retinex(
    input_path,
    output_path=None,
    sigmas=SIGMAS_MSR
):
    """
    Apply Multi-Scale Retinex using several Gaussian scales.

    Large scales use reduced-resolution illumination estimation
    to improve performance. The remaining algorithm, normalization,
    colour reconstruction, and luminance blending are retained.
    """
    if not sigmas:
        raise ValueError("At least one Retinex scale is required.")

    if any(sigma <= 0 for sigma in sigmas):
        raise ValueError("All Retinex scales must be positive.")

    image = load_image(input_path)

    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    original_luminance = lab[:, :, 0].astype(np.float32)

    luminance = original_luminance + EPSILON

    retinex = np.zeros_like(luminance, dtype=np.float32)

    # Compute Retinex responses at multiple scales.
    for sigma in sigmas:
        illumination = estimate_illumination(
            luminance, float(sigma)
        )

        scale_response = (
            np.log(luminance)
            - np.log(illumination)
        )

        retinex += scale_response

    # Average the responses from the selected scales.
    retinex /= float(len(sigmas))

    # Robust normalization.
    normalized = percentile_normalize(retinex)
    retinex_luminance = normalized * 255.0

    # Blend with original luminance to avoid excessive brightening.
    enhanced_luminance = (
        ORIGINAL_WEIGHT * original_luminance
        + RETINEX_WEIGHT * retinex_luminance
    )

    enhanced = reconstruct_from_luminance(
        lab, enhanced_luminance
    )

    if output_path is not None:
        save_image(enhanced, output_path)

    return enhanced


# ============================================================
# IMAGE SAVING
# ============================================================

def save_image(image, output_path):
    """Save an image and report any write failure."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    success = cv2.imwrite(str(output_path), image)

    if not success:
        raise ValueError(f"Could not save output image: {output_path}")

    return str(output_path)


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":
    import time

    project_root = Path(__file__).resolve().parent.parent
    input_path = project_root / "uploads" / "dark.jpg"
    output_path = project_root / "uploads" / "msr_test_output.jpg"

    if not input_path.exists():
        print(f"Place a test image at: {input_path}")
    else:
        start = time.perf_counter()

        multi_scale_retinex(
            input_path,
            output_path,
            SIGMAS_MSR
        )

        elapsed = time.perf_counter() - start

        print("MSR completed successfully.")
        print(f"Output: {output_path}")
        print(f"Processing time: {elapsed:.3f} seconds")