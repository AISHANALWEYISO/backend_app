from flask import Blueprint, request, jsonify
from app import db
from app.models.tips import Tip
from flask_jwt_extended import jwt_required, get_jwt_identity

tips_bp = Blueprint('tips', __name__)


# ---------------------------
# Get All Tips
# ---------------------------
@tips_bp.route('/', methods=['GET'])
def get_all_tips():
    tips = Tip.query.all()
    return jsonify({
        "tips": [tip.to_dict() for tip in tips],
        "count": len(tips)
    }), 200


# ---------------------------
# Get Single Tip by ID
# ---------------------------
@tips_bp.route('/<int:id>', methods=['GET'])
def get_tip(id):
    tip = Tip.query.get_or_404(id)
    return jsonify({"tip": tip.to_dict()}), 200


# ---------------------------
# Create New Tip (Protected)
# ---------------------------
@tips_bp.route('/create', methods=['POST'])
@jwt_required()
def create_tip():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No input data provided"}), 400

    name = data.get("name")
    image_url = data.get("image_url")
    description = data.get("description")
    content = data.get("content")

    if not all([name, image_url, description]):
        return jsonify({"message": "Name, image, and description are required"}), 400

    new_tip = Tip(
        name=name,
        image_url=image_url,
        description=description,
        content=content
    )

    db.session.add(new_tip)
    db.session.commit()

    return jsonify({
        "message": "Tip created successfully",
        "tip": new_tip.to_dict()
    }), 201


# ---------------------------
# Update Tip (Protected)
# ---------------------------
@tips_bp.route('/edit/<int:id>', methods=['PUT'])
@jwt_required()
def update_tip(id):
    tip = Tip.query.get_or_404(id)
    data = request.get_json()

    if not data:
        return jsonify({"message": "No input data provided"}), 400

    tip.name = data.get("name", tip.name)
    tip.image_url = data.get("image_url", tip.image_url)
    tip.description = data.get("description", tip.description)
    tip.content = data.get("content", tip.content)

    db.session.commit()

    return jsonify({
        "message": "Tip updated successfully",
        "tip": tip.to_dict()
    }), 200


# ---------------------------
# Delete Tip (Protected)
# ---------------------------
@tips_bp.route('/delete/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_tip(id):
    tip = Tip.query.get_or_404(id)

    db.session.delete(tip)
    db.session.commit()

    return jsonify({"message": "Tip deleted successfully"}), 200