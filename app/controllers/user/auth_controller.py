from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)
from werkzeug.security import generate_password_hash
from services.otp_service import send_otp_email, verify_otp

auth_bp = Blueprint('auth', __name__)


# ── Register ──
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    name = data.get("name")
    age = data.get("age")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    usertype = "Farmer"

    if not all([name, email, password, confirm_password]):
        return jsonify({"message": "Missing required fields"}), 400

    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    new_user = User(name=name, age=age, email=email, usertype=usertype)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Account created successfully!"}), 201


# ── Login ──
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"message": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "Sign Up to continue"}), 401

    if not user.check_password(password):
        return jsonify({"message": "Incorrect password"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "usertype": user.usertype
        }
    }), 200


# ── Send OTP ──
@auth_bp.route('/forgot-password/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    email = data.get("email")
    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()

    # Tell user clearly if email doesn't exist
    if not user:
        return jsonify({"message": "Email does not exist", "success": False}), 404

    result = send_otp_email(email)

    if result["success"]:
        return jsonify({"message": "OTP sent to your email", "success": True}), 200
    else:
        return jsonify({"message": "Failed to send OTP. Try again later", "success": False}), 500


# ── Verify OTP ──
@auth_bp.route('/forgot-password/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    email = data.get("email")
    otp = data.get("otp")

    if not email or not otp:
        return jsonify({"message": "Email and OTP are required"}), 400

    result = verify_otp(email, otp)

    if result["success"]:
        return jsonify({"message": "OTP verified", "success": True}), 200
    else:
        return jsonify({"message": result["message"], "success": False}), 400


# ── Reset Password ──
@auth_bp.route('/forgot-password/reset', methods=['POST'])
def reset_password():
    data = request.get_json()
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    email = data.get("email")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not all([email, new_password, confirm_password]):
        return jsonify({"message": "All fields are required"}), 400

    if new_password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "Email does not exist"}), 404

    user.password = generate_password_hash(new_password)
    db.session.commit()

    return jsonify({"message": "Password reset successfully! Please sign in."}), 200


# ── Refresh Token ──
@auth_bp.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token}), 200