# from flask import Blueprint, request, jsonify
# from app import db
# from app.models.user import User
# from flask_jwt_extended import create_access_token , get_jwt_identity, jwt_required

# auth_bp = Blueprint('auth', __name__)

# ## sign up
# @auth_bp.route('/register', methods=['POST'])
# def register():

#     data = request.get_json()

#     name = data.get("name")
#     age = data.get("age")
#     email = data.get("email")
#     password = data.get("password")
#     confirm_password = data.get("confirm_password")
#     usertype = data.get("usertype")

#     if password != confirm_password:
#         return jsonify({"message": "Passwords do not match"}), 400

#     if User.query.filter_by(email=email).first():
#         return jsonify({"message": "Email already exists"}), 400

#     new_user = User(
#         name=name,
#         age=age,
#         email=email,
#         usertype=usertype
#     )

#     new_user.set_password(password)

#     db.session.add(new_user)
#     db.session.commit()

#     return jsonify({
#         "message": "User registered successfully"
#     }), 201

# ## sign in
# @auth_bp.route('/login', methods=['POST'])
# def login():

#     data = request.get_json()

#     email = data.get("email")
#     password = data.get("password")

#     user = User.query.filter_by(email=email).first()

#     if not user or not user.check_password(password):
#         return jsonify({
#             "message": "Invalid email or password"
#         }), 401

#     token = create_access_token(identity=user.id)

#     return jsonify({
#         "message": "Login successful",
#         "token": token,
#         "user": {
#             "id": user.id,
#             "name": user.name,
#             "email": user.email,
#             "usertype": user.usertype
#         }
#     })

# ## forgot password
# @auth_bp.route('/forgot_password', methods=['POST'])
# def forgot_password():

#     data = request.get_json()
#     email = data.get("email")

#     user = User.query.filter_by(email=email).first()

#     if not user:
#         return jsonify({"message": "Email not found"}), 404

#     return jsonify({
#         "message": "Password reset instructions sent"
#     })


# @auth_bp.route("/token/refresh", methods=["POST"])
# @jwt_required(refresh=True)  # this ensures a refresh token is required
# def refresh():
#     identity = get_jwt_identity()  # gets the identity from the refresh token
#     access_token = create_access_token(identity=identity)
#     return jsonify({"access_token": access_token}), 200


from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity, 
    jwt_required
)

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


# User Registration
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
    usertype = data.get("usertype")

    # Basic validation to ensure fields exist
    if not all([name, email, password, confirm_password]):
        return jsonify({"message": "Missing required fields"}), 400

    # Password validation
    if password != confirm_password:
        return jsonify({"message": "Passwords do not match"}), 400

    # Check if email exists
    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    # Create new user
    new_user = User(
        name=name,
        age=age,
        email=email,
        usertype=usertype
    )
    
    # Assuming your User model has a set_password method that hashes the password
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# User Login
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

    # Check user existence and password validity
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid email or password"}), 401

    # FIX: Convert user.id (usually an int) to a string for JWT identity
    user_id_str = str(user.id)

    # Create tokens
    access_token = create_access_token(identity=user_id_str)
    refresh_token = create_refresh_token(identity=user_id_str)

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


# Forgot Password (placeholder)
@auth_bp.route('/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    email = data.get("email")

    if not email:
        return jsonify({"message": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    
    if not user:
        # Return 200 anyway to prevent email enumeration attacks (security best practice)
        # Or keep 404 if you prefer strict feedback as per your original code
        return jsonify({"message": "If that email exists, instructions have been sent."}), 200

    # TODO: implement actual email sending logic here
    # send_reset_email(user.email)

    return jsonify({"message": "Password reset instructions sent"}), 200


# Refresh Token
@auth_bp.route("/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    # This will now return a string because we stored it as a string during login
    identity = get_jwt_identity()
    
    # Create a new access token with the same identity
    new_access_token = create_access_token(identity=identity)
    
    return jsonify({"access_token": new_access_token}), 200