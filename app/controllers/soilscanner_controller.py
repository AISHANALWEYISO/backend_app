from flask import request, jsonify
from services.soil_scanner import analyze_soil_image

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE_MB = 10

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_media_type(filename: str) -> str:
    ext = filename.rsplit(".", 1)[1].lower()
    mapping = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }
    return mapping.get(ext, "image/jpeg")

def scan_soil():
    """
    POST /api/soil/analyze
    Accepts a multipart image upload, returns AI soil analysis.
    """
    # Check file is present
    if "image" not in request.files:
        return jsonify({"error": "No image file provided. Send image as 'image' field."}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    # Read image bytes
    image_data = file.read()

    # Check file size
    size_mb = len(image_data) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        return jsonify({"error": f"File too large. Max size is {MAX_FILE_SIZE_MB}MB."}), 400

    media_type = get_media_type(file.filename)

    # Run AI analysis
    result = analyze_soil_image(image_data, media_type)

    if result is None:
        return jsonify({"error": "Failed to analyze soil image. Please try again."}), 500

    return jsonify({
        "success": True,
        "analysis": result
    }), 200