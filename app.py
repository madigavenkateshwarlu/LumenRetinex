from pathlib import Path
from time import perf_counter
from uuid import uuid4

import cv2
import numpy as np
from flask import Flask, jsonify, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from algorithms.logarithmic import logarithmic_enhancement
from algorithms.retinex import (
    single_scale_retinex,
    multi_scale_retinex,
)
from algorithms.decomposition import illumination_reflectance_decomposition


# ============================================================
# LumenRetinex - Flask Application
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "webp"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 15 * 1024 * 1024


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def image_statistics(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return {
        "brightness": round(float(np.mean(gray)), 2),
        "contrast": round(float(np.std(gray)), 2),
        "width": int(image.shape[1]),
        "height": int(image.shape[0]),
    }


def enhance_image(input_path, output_path, method):
    """Run the selected enhancement algorithm."""

    if method == "logarithmic":
        result = logarithmic_enhancement(
            input_path, output_path
        )

    elif method == "ssr":
        result = single_scale_retinex(
            input_path, output_path
        )

    elif method == "msr":
        result = multi_scale_retinex(
            input_path, output_path
        )

    elif method == "decomposition":
        result = illumination_reflectance_decomposition(
            input_path, UPLOAD_DIR
        )

        # The decomposition function may return
        # illumination, reflectance and enhanced image.
        if isinstance(result, tuple):
            result = result[-1]

        if result is None:
            result = cv2.imread(str(output_path))

        if result is None:
            raise ValueError(
                "Decomposition did not return an enhanced image."
            )

        if not cv2.imwrite(str(output_path), result):
            raise ValueError("Could not save decomposition output.")

    else:
        raise ValueError("Please select a valid enhancement method.")

    # Some implementations return the enhanced image;
    # others only save it to disk.
    if result is None:
        result = cv2.imread(str(output_path))

    if result is None:
        raise ValueError(
            "Enhancement failed. No output image was generated."
        )

    # Ensure the returned result is saved to the requested path.
    if not cv2.imwrite(str(output_path), result):
        raise ValueError("Could not save the enhanced image.")

    return result


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/enhance", methods=["POST"])
def enhance():
    start_time = perf_counter()

    try:
        # Accept either common upload field name.
        uploaded_file = (
            request.files.get("image")
            or request.files.get("file")
        )

        if uploaded_file is None or not uploaded_file.filename:
            return jsonify({
                "error": "Please upload an image."
            }), 400

        if not allowed_file(uploaded_file.filename):
            return jsonify({
                "error": "Unsupported image format."
            }), 400

        method = request.form.get(
            "method", "msr"
        ).strip().lower()

        valid_methods = {
            "logarithmic", "ssr", "msr", "decomposition"
        }

        if method not in valid_methods:
            return jsonify({
                "error": "Invalid enhancement method."
            }), 400

        # Generate unique filenames to avoid overwriting uploads.
        image_id = uuid4().hex
        safe_name = secure_filename(uploaded_file.filename)
        extension = Path(safe_name).suffix.lower() or ".jpg"

        input_name = f"{image_id}_original{extension}"
        output_name = f"{image_id}_enhanced.png"

        input_path = UPLOAD_DIR / input_name
        output_path = UPLOAD_DIR / output_name

        uploaded_file.save(str(input_path))

        original = cv2.imread(str(input_path))

        if original is None:
            return jsonify({
                "error": "The uploaded file is not a valid image."
            }), 400

        enhanced = enhance_image(
            input_path, output_path, method
        )

        before = image_statistics(original)
        after = image_statistics(enhanced)

        elapsed = round(perf_counter() - start_time, 3)

        return jsonify({
            "success": True,
            "method": method,
            "original": f"/uploads/{input_name}",
            "enhanced": f"/uploads/{output_name}",
            "brightness_before": before["brightness"],
            "brightness_after": after["brightness"],
            "contrast_before": before["contrast"],
            "contrast_after": after["contrast"],
            "processing_time": elapsed,
            "width": after["width"],
            "height": after["height"],
            "download": f"/uploads/{output_name}",
        })

    except (ValueError, cv2.error) as error:
        return jsonify({"error": str(error)}), 400

    except Exception:
        app.logger.exception("Image enhancement failed")
        return jsonify({
            "error": "Enhancement failed. Check the terminal for details."
        }), 500


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(
        str(UPLOAD_DIR),
        filename,
        as_attachment=False
    )


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "Image is too large. Maximum size is 15 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True)