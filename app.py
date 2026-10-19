from pathlib import Path
from time import perf_counter
from uuid import uuid4

import cv2
import numpy as np
from flask import (
    Flask,
    jsonify,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from werkzeug.utils import secure_filename

from algorithms.logarithmic import logarithmic_enhancement
from algorithms.retinex import (
    single_scale_retinex,
    multi_scale_retinex,
)
from algorithms.decomposition import illumination_reflectance_decomposition


# ============================================================
# APPLICATION CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff"}

MAX_UPLOAD_BYTES = 20 * 1024 * 1024  # 20 MB

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES


# ============================================================
# HELPERS
# ============================================================

def allowed_file(filename):
    """Check the uploaded file extension."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def image_metrics(image):
    """Calculate descriptive brightness and contrast measurements."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return {
        "brightness": round(float(np.mean(gray)), 2),
        "contrast": round(float(np.std(gray)), 2),
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
    }


def normalize_method(method):
    """Accept common method names from frontend controls."""
    method = (method or "").strip().lower()

    aliases = {
        "log": "logarithmic",
        "log_transform": "logarithmic",
        "logarithmic_transform": "logarithmic",
        "ssr": "ssr",
        "single_scale_retinex": "ssr",
        "msr": "msr",
        "multi_scale_retinex": "msr",
        "decomposition": "decomposition",
        "illumination_reflectance": "decomposition",
    }

    return aliases.get(method, method)


def save_uploaded_image(file_storage):
    """Save an uploaded file using a generated safe filename."""
    original_name = secure_filename(file_storage.filename or "")

    if not original_name:
        raise ValueError("Please choose an image file.")

    if not allowed_file(original_name):
        raise ValueError(
            "Unsupported image format. Use JPG, PNG, BMP, or TIFF."
        )

    extension = Path(original_name).suffix.lower()
    filename = f"input_{uuid4().hex}{extension}"
    input_path = UPLOAD_DIR / filename

    file_storage.save(str(input_path))

    # Verify that OpenCV can decode the file.
    image = cv2.imread(str(input_path), cv2.IMREAD_COLOR)

    if image is None or image.size == 0:
        input_path.unlink(missing_ok=True)
        raise ValueError("The uploaded file is not a valid image.")

    return input_path, image


def run_enhancement(method, input_path, output_path):
    """Dispatch the selected method and return the enhanced image."""
    if method == "logarithmic":
        # Keep the argument style consistent with your existing
        # logarithmic.py implementation.
        result = logarithmic_enhancement(
            str(input_path),
            str(output_path)
        )

        # Support functions that either save the file or return an array.
        if isinstance(result, np.ndarray):
            return result

        image = cv2.imread(str(output_path), cv2.IMREAD_COLOR)
        if image is None:
            raise RuntimeError(
                "Logarithmic transformation did not create an output image."
            )
        return image

    if method == "ssr":
        return single_scale_retinex(
            str(input_path),
            str(output_path)
        )

    if method == "msr":
        return multi_scale_retinex(
            str(input_path),
            str(output_path)
        )

    if method == "decomposition":
        _, _, enhanced_image = illumination_reflectance_decomposition(
            str(input_path),
            str(output_path.parent)
        )

        if not cv2.imwrite(str(output_path), enhanced_image):
            raise RuntimeError(
                "Could not save the decomposition output image."
            )
        return enhanced_image

    raise ValueError(
        "Unknown method. Choose logarithmic, ssr, msr, or decomposition."
    )


# ============================================================
# ROUTES
# ============================================================

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/enhance", methods=["POST"])
def enhance():
    input_path = None
    output_path = None

    try:
        uploaded_file = request.files.get("image")

        if uploaded_file is None:
            uploaded_file = request.files.get("file")

        if uploaded_file is None or not uploaded_file.filename:
            return jsonify({
                "success": False,
                "error": "Please upload an image first."
            }), 400

        method = normalize_method(request.form.get("method", "msr"))

        valid_methods = {
            "logarithmic",
            "ssr",
            "msr",
            "decomposition",
        }

        if method not in valid_methods:
            return jsonify({
                "success": False,
                "error": f"Unsupported enhancement method: {method}"
            }), 400

        input_path, original_image = save_uploaded_image(uploaded_file)

        output_filename = f"enhanced_{uuid4().hex}.png"
        output_path = UPLOAD_DIR / output_filename

        original_metrics = image_metrics(original_image)

        # Measure the enhancement operation separately from upload,
        # input decoding, and the browser's image display.
        start = perf_counter()

        enhanced_image = run_enhancement(
            method,
            input_path,
            output_path
        )

        processing_time = perf_counter() - start

        if enhanced_image is None or not isinstance(
            enhanced_image, np.ndarray
        ):
            raise RuntimeError("The enhancement algorithm returned no image.")

        if enhanced_image.size == 0:
            raise RuntimeError("The enhancement output is empty.")

        # Ensure output exists, even if an algorithm returned an array
        # without saving it.
        if not output_path.exists():
            if not cv2.imwrite(str(output_path), enhanced_image):
                raise RuntimeError("Could not save the enhanced image.")

        enhanced_metrics = image_metrics(enhanced_image)

        original_url = url_for(
            "uploaded_file",
            filename=input_path.name
        )
        enhanced_url = url_for(
            "uploaded_file",
            filename=output_path.name
        )

        # Include common field aliases to simplify frontend integration.
        return jsonify({
            "success": True,
            "method": method,
            "original_url": original_url,
            "enhanced_url": enhanced_url,
            "output_url": enhanced_url,
            "download_url": url_for(
                "download_file",
                filename=output_path.name
            ),
            "processing_time": round(processing_time, 4),
            "original": original_metrics,
            "enhanced": enhanced_metrics,
            "brightness_before": original_metrics["brightness"],
            "brightness_after": enhanced_metrics["brightness"],
            "contrast_before": original_metrics["contrast"],
            "contrast_after": enhanced_metrics["contrast"],
            "width": enhanced_metrics["width"],
            "height": enhanced_metrics["height"],
        })

    except ValueError as exc:
        return jsonify({
            "success": False,
            "error": str(exc)
        }), 400

    except Exception as exc:
        app.logger.exception("Image enhancement failed")
        return jsonify({
            "success": False,
            "error": "Image enhancement failed. Check the server terminal."
        }), 500


@app.route("/uploads/<path:filename>", methods=["GET"])
def uploaded_file(filename):
    return send_from_directory(
        str(UPLOAD_DIR),
        filename,
        as_attachment=False
    )


@app.route("/download/<path:filename>", methods=["GET"])
def download_file(filename):
    return send_from_directory(
        str(UPLOAD_DIR),
        filename,
        as_attachment=True
    )


@app.errorhandler(413)
def file_too_large(_error):
    return jsonify({
        "success": False,
        "error": "Image is too large. Maximum upload size is 20 MB."
    }), 413


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )