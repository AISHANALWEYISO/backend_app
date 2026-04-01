from flask import Blueprint
from app.controllers.soilscanner_controller import scan_soil

soil_bp = Blueprint("soil", __name__)

# POST /api/soil/analyze
soil_bp.route("/soil/analyze", methods=["POST"])(scan_soil)

# """
# soil_routes.py
# --------------
# Endpoints for soil photo analysis.
# """

# import os
# from flask import Blueprint, request, jsonify
# from app.controllers.soilscanner_controller import SoilController

# soil_bp = Blueprint('soil', __name__, url_prefix='/api/soil')

# GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')


# # ── POST /api/soil/analyse ────────────────────────────────────────────────────
# # Accepts: multipart/form-data
# #   - image  : the soil photo file
# #   - region : Central | Eastern | Northern | Western
# #   - season : Rainy | Dry
# #
# # Returns crop recommendations based on Uganda localised model
# @soil_bp.route('/analyse', methods=['POST'])
# def analyse_soil():
#     # Validate image
#     if 'image' not in request.files:
#         return jsonify({'error': 'No image provided. Send image as multipart/form-data'}), 400

#     image_file = request.files['image']
#     if image_file.filename == '':
#         return jsonify({'error': 'Empty image file'}), 400

#     # Validate region and season
#     region = request.form.get('region', '').strip()
#     season = request.form.get('season', '').strip()

#     if not region:
#         return jsonify({'error': 'region is required (Central, Eastern, Northern, Western)'}), 400
#     if not season:
#         return jsonify({'error': 'season is required (Rainy or Dry)'}), 400

#     # Read image bytes
#     image_bytes = image_file.read()

#     # Run full pipeline
#     result = SoilController.analyse_soil_photo(
#         image_bytes=image_bytes,
#         region=region,
#         season=season,
#         gemini_api_key=GEMINI_API_KEY,
#     )

#     if not result['success']:
#         return jsonify({'error': result['error']}), 500

#     return jsonify(result), 200


# # ── POST /api/soil/recommend ──────────────────────────────────────────────────
# # If you already know the soil type and just want crop recommendations
# # Body (JSON): { "soil_type": "Loam", "region": "Central", "season": "Rainy" }
# @soil_bp.route('/recommend', methods=['POST'])
# def recommend_only():
#     data = request.get_json()
#     if not data:
#         return jsonify({'error': 'No data provided'}), 400

#     soil_type = data.get('soil_type', '')
#     region    = data.get('region', '')
#     season    = data.get('season', '')

#     if not all([soil_type, region, season]):
#         return jsonify({'error': 'soil_type, region and season are all required'}), 400

#     result = SoilController.recommend_crops(soil_type, region, season)

#     if not result['success']:
#         return jsonify({'error': result['error']}), 422

#     return jsonify(result), 200