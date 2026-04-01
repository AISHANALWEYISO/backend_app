# app/controllers/user/user_controller.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User

# ✅ Create the blueprint
user_bp = Blueprint('user', __name__)


# ── Check Soil Scanner Credits ──
@user_bp.route('/soil-scanner-access', methods=['GET'])
@jwt_required()
def check_soil_scanner_access():
    """
    Mobile app calls this to check if user has credits
    URL: GET /api/user/soil-scanner-access
    """
    try:
        # 1. Get logged-in user ID from JWT
        current_user_id = get_jwt_identity()
        
        # 2. Find user in database
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        # 3. Get credits
       
        credits = user.soil_scan_credits if user.soil_scan_credits is not None else 0
        
        # 4. Check if they have access (1 or more credits)
        has_access = credits > 0
        
        # 5. Return response
        return jsonify({
            "success": True,
            "has_access": has_access,
            "credits_remaining": credits
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ── Update Profile (Optional - for future) ──
@user_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    # TODO: Implement profile update
    return jsonify({"success": True, "message": "Profile update endpoint"}), 200