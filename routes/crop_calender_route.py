from flask import Blueprint, request, jsonify
from app.controllers.cropcalender import CropController
 
crops_bp = Blueprint('crops', __name__, url_prefix='/api/crops')
 
 
# ── GET /api/crops ─────────────────────────────────────────────────────────────
# Returns all crops. Optional query param: ?season=rainy
@crops_bp.route('', methods=['GET'])
def get_all_crops():
    season = request.args.get('season')
    if season:
        data = CropController.get_crops_by_season(season)
    else:
        data = CropController.get_all_crops()
    return jsonify(data), 200
 
 
# ── GET /api/crops/<id> ────────────────────────────────────────────────────────
@crops_bp.route('/<int:crop_id>', methods=['GET'])
def get_crop(crop_id):
    crop = CropController.get_crop_by_id(crop_id)
    if not crop:
        return jsonify({'error': 'Crop not found'}), 404
    return jsonify(crop), 200
 
 
# ── POST /api/crops ────────────────────────────────────────────────────────────
# Body (JSON):
# {
#   "name": "Maize",
#   "planting_time": "Mar – Apr",
#   "harvest_time": "Jun – Jul",
#   "duration": "3 – 4 months",
#   "season": "Rainy Season",
#   "tip": "Apply DAP at planting.",
#   "color": "#F9A825"
# }
@crops_bp.route('', methods=['POST'])
def create_crop():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
 
    crop, error = CropController.create_crop(data)
    if error:
        return jsonify({'error': error}), 422
    return jsonify(crop), 201
 
 
# ── PUT /api/crops/<id> ────────────────────────────────────────────────────────
@crops_bp.route('/<int:crop_id>', methods=['PUT'])
def update_crop(crop_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
 
    crop, error = CropController.update_crop(crop_id, data)
    if error:
        return jsonify({'error': error}), 404
    return jsonify(crop), 200
 
 
# ── DELETE /api/crops/<id> ─────────────────────────────────────────────────────
@crops_bp.route('/<int:crop_id>', methods=['DELETE'])
def delete_crop(crop_id):
    deleted = CropController.delete_crop(crop_id)
    if not deleted:
        return jsonify({'error': 'Crop not found'}), 404
    return jsonify({'message': 'Crop deleted successfully'}), 200