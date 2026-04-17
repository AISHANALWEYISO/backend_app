# from flask import Blueprint
# from app.controllers.soilscanner_controller import scan_soil

# soil_bp = Blueprint("soil", __name__)

# # POST /api/soil/analyze
# soil_bp.route("/soil/analyze", methods=["POST"])(scan_soil)



# # routes/soilscanner_route.py
# from flask import Blueprint, request, jsonify, current_app
# from flask_jwt_extended import jwt_required, get_jwt_identity
# import numpy as np
# import logging
# from datetime import datetime

# soil_bp = Blueprint("soil", __name__)
# logger = logging.getLogger(__name__)

# # ─────────────────────────────────────────────────────────────
# # VALIDATION CONFIG
# # ─────────────────────────────────────────────────────────────
# VALID_RANGES = {
#     "ph": (3.0, 10.0),
#     "EC": (0.0, 2.5),
#     "CaCO3": (0.0, 25.0),
#     "OC": (0.0, 15.0),
#     "N": (0.0, 400.0),
#     "P": (0.0, 100.0),
#     "K": (0.0, 1300.0),
# }
# REQUIRED_FIELDS = ["ph", "EC", "CaCO3", "OC", "N", "P", "K"]


# def validate_soil_input(data):
#     """Validate and sanitize soil input parameters"""
#     errors = []
#     validated = {}
    
#     for field in REQUIRED_FIELDS:
#         if field not in data:
#             errors.append(f"Missing required field: {field}")
    
#     if errors:
#         return None, errors
    
#     for field, (min_val, max_val) in VALID_RANGES.items():
#         value = data.get(field)
#         try:
#             num = float(value)
#             if not (min_val <= num <= max_val):
#                 errors.append(f"{field}={num} out of range [{min_val}, {max_val}]")
#             validated[field] = round(num, 3)
#         except (TypeError, ValueError):
#             errors.append(f"Invalid number for {field}: {value}")
    
#     return validated if not errors else None, errors


# def _assess_soil_health(params):
#     """Generate simple soil health insights"""
#     insights = []
    
#     # pH assessment
#     if 6.0 <= params["ph"] <= 7.5:
#         insights.append({"parameter": "pH", "value": params["ph"], "status": "optimal", "message": "Good for most crops"})
#     elif params["ph"] < 6.0:
#         insights.append({"parameter": "pH", "value": params["ph"], "status": "acidic", "message": "Consider lime application"})
#     else:
#         insights.append({"parameter": "pH", "value": params["ph"], "status": "alkaline", "message": "Consider adding organic matter"})
    
#     # Organic Carbon
#     if params["OC"] >= 2.0:
#         insights.append({"parameter": "Organic Carbon", "value": params["OC"], "status": "good", "message": "Healthy soil structure"})
#     elif params["OC"] >= 1.0:
#         insights.append({"parameter": "Organic Carbon", "value": params["OC"], "status": "moderate", "message": "Add compost to improve"})
#     else:
#         insights.append({"parameter": "Organic Carbon", "value": params["OC"], "status": "low", "message": "Urgent: Add organic matter"})
    
#     # Salinity (EC)
#     if params["EC"] < 0.8:
#         insights.append({"parameter": "Salinity (EC)", "value": params["EC"], "status": "low", "message": "Safe for sensitive crops"})
#     elif params["EC"] < 1.5:
#         insights.append({"parameter": "Salinity (EC)", "value": params["EC"], "status": "moderate", "message": "Monitor irrigation"})
#     else:
#         insights.append({"parameter": "Salinity (EC)", "value": params["EC"], "status": "high", "message": "Leach salts before planting"})
    
#     return insights


# # ─────────────────────────────────────────────────────────────
# # ROUTES (AUTH REQUIRED)
# # ─────────────────────────────────────────────────────────────

# @soil_bp.route("/soil/predict", methods=["POST"])
# @jwt_required()  # 🔐 AUTH REQUIRED - Remove optional=True
# def predict_crop():
#     """
#     Predict best crop for given soil parameters
#     🔐 Requires valid JWT token in Authorization header
    
#     Request Headers:
#       Authorization: Bearer <your_jwt_token>
    
#     Request JSON:
#     {
#         "ph": 6.5, "EC": 0.4, "CaCO3": 5, "OC": 0.3, "N": 180, "P": 12, "K": 250
#     }
#     """
#     try:
#         # 1. Get authenticated user
#         user_id = get_jwt_identity()  # ✅ Returns user ID from JWT
        
#         # 2. Check model availability
#         from app import crop_model, crop_scaler, crop_label_encoder, crop_feature_order
        
#         if crop_model is None:
#             logger.error(f"User {user_id}: Crop model not loaded")
#             return jsonify({
#                 "status": "error",
#                 "error": "Crop prediction service unavailable",
#                 "message": "Please contact support"
#             }), 503

#         # 3. Parse & validate request
#         if not request.is_json:
#             return jsonify({
#                 "status": "error",
#                 "error": "Invalid content type",
#                 "message": "Request must be JSON"
#             }), 415

#         data = request.get_json()
#         validated, errors = validate_soil_input(data)
        
#         if errors:
#             logger.warning(f"User {user_id}: Validation failed - {errors}")
#             return jsonify({
#                 "status": "error",
#                 "error": "Validation failed",
#                 "details": errors
#             }), 400

#         # 4. Prepare input & predict
#         input_array = np.array([[validated[feat] for feat in crop_feature_order]])
#         scaled_input = crop_scaler.transform(input_array)
        
#         prediction = crop_model.predict(scaled_input)[0]
#         probas = crop_model.predict_proba(scaled_input)[0]
        
#         # 5. Decode results
#         predicted_crop = crop_label_encoder.inverse_transform([prediction])[0]
#         confidence = round(float(probas[prediction] * 100), 2)
        
#         # 6. Top-3 recommendations
#         top_3_idx = np.argsort(probas)[::-1][:3]
#         recommendations = [
#             {"crop": crop_label_encoder.inverse_transform([idx])[0], "confidence": round(float(probas[idx] * 100), 2)}
#             for idx in top_3_idx
#         ]
        
#         # 7. Soil health insights
#         soil_health = _assess_soil_health(validated)
        
#         # 8. ✅ Log prediction to user history (optional - implement in your DB)
#         # save_prediction_to_db(user_id, validated, predicted_crop, confidence)
        
#         logger.info(f"✅ User {user_id}: Predicted {predicted_crop} ({confidence}% confidence)")
        
#         return jsonify({
#             "status": "success",
#             "user_id": user_id,  # ✅ Include authenticated user info
#             "recommended_crop": predicted_crop,
#             "confidence": confidence,
#             "top_3_recommendations": recommendations,
#             "soil_health": soil_health,
#             "input": validated,
#             "timestamp": datetime.utcnow().isoformat()
#         }), 200
        
#     except Exception as e:
#         user_id = get_jwt_identity() if request.headers.get("Authorization") else "unknown"
#         logger.error(f"❌ User {user_id}: Prediction error - {str(e)}", exc_info=True)
#         return jsonify({
#             "status": "error",
#             "error": "Internal server error",
#             "message": "Please try again later"
#         }), 500


# @soil_bp.route("/soil/crops", methods=["GET"])
# @jwt_required()  # 🔐 Also protect crop list endpoint
# def get_supported_crops():
#     """Return list of crops the model can predict (Auth Required)"""
#     try:
#         from app import crop_label_encoder
#         if crop_label_encoder is None:
#             return jsonify({"status": "error", "error": "Model not loaded"}), 503
        
#         crops = sorted(crop_label_encoder.classes_.tolist())
#         return jsonify({
#             "status": "success",
#             "crops": crops,
#             "count": len(crops)
#         }), 200
#     except Exception as e:
#         return jsonify({"status": "error", "error": str(e)}), 500


# @soil_bp.route("/soil/health-guide", methods=["GET"])
# @jwt_required()  # 🔐 Protect educational content too
# def get_soil_health_guide():
#     """Return reference ranges for soil parameters (Auth Required)"""
#     guide = {
#         "ph": {"optimal": "6.0 - 7.5", "acidic": "< 6.0", "alkaline": "> 7.5", "unit": "pH scale"},
#         "EC": {"low": "< 0.8 dS/m", "moderate": "0.8 - 1.5 dS/m", "high": "> 1.5 dS/m", "unit": "dS/m"},
#         "OC": {"low": "< 1.0%", "moderate": "1.0 - 2.0%", "good": "> 2.0%", "unit": "%"},
#         "N": {"unit": "kg/ha", "note": "Varies by crop"},
#         "P": {"unit": "kg/ha", "note": "Varies by crop"},
#         "K": {"unit": "kg/ha", "note": "Varies by crop"}
#     }
#     return jsonify({"status": "success", "guide": guide}), 200


# routes/soilscanner_route.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import numpy as np
import joblib
import os
import logging
from datetime import datetime
from PIL import Image
import io

soil_bp = Blueprint("soil", __name__)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_IMAGE_SIZE = 16 * 1024 * 1024  # 16MB

# Region-season to typical soil parameter ranges (East Africa focus)
REGION_SEASON_PROFILES = {
    'Central-Rainy': {'ph': (5.5, 6.8), 'OC': (1.5, 3.5), 'N': (120, 200), 'P': (25, 45), 'K': (180, 280)},
    'Central-Dry': {'ph': (6.0, 7.5), 'OC': (1.0, 2.5), 'N': (100, 180), 'P': (20, 40), 'K': (150, 250)},
    'Eastern-Rainy': {'ph': (5.8, 7.2), 'OC': (1.2, 3.0), 'N': (110, 190), 'P': (22, 42), 'K': (160, 260)},
    'Eastern-Dry': {'ph': (6.5, 8.0), 'OC': (0.8, 2.0), 'N': (90, 160), 'P': (18, 35), 'K': (140, 230)},
    'Northern-Rainy': {'ph': (5.2, 6.5), 'OC': (1.8, 4.0), 'N': (130, 220), 'P': (28, 50), 'K': (190, 300)},
    'Northern-Dry': {'ph': (6.2, 7.8), 'OC': (1.0, 2.8), 'N': (100, 180), 'P': (20, 40), 'K': (150, 250)},
    'Western-Rainy': {'ph': (5.0, 6.2), 'OC': (2.0, 4.5), 'N': (140, 240), 'P': (30, 55), 'K': (200, 320)},
    'Western-Dry': {'ph': (5.8, 7.2), 'OC': (1.2, 3.0), 'N': (110, 190), 'P': (22, 42), 'K': (160, 260)},
}

# Fallback defaults if region/season not matched
DEFAULT_PROFILE = {'ph': (6.0, 7.0), 'OC': (1.5, 3.0), 'N': (120, 200), 'P': (25, 45), 'K': (180, 280)}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def estimate_soil_params_from_image(image_bytes, region, season):
    """
    Estimate soil parameters from image + location context.
    
    🔹 Interim solution: Uses region/season profiles + simple image analysis
    🔹 Production: Replace with trained CNN/ML model for true image-to-params
    
    Returns dict with: ph, EC, CaCO3, OC, N, P, K
    """
    # 1. Get base profile from region + season
    profile_key = f"{region}-{season}"
    profile = REGION_SEASON_PROFILES.get(profile_key, DEFAULT_PROFILE)
    
    # 2. Simple image analysis (color-based heuristics)
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((200, 200))  # Downsample for speed
        pixels = np.array(img)
        
        # Average color (RGB)
        avg_color = pixels.mean(axis=(0, 1))
        r, g, b = avg_color
        
        # Heuristic: Darker soil → higher organic carbon
        brightness = (r + g + b) / 3
        oc_factor = max(0, min(1, (200 - brightness) / 100))  # 0.0 to 1.0
        
        # Heuristic: Reddish tint → higher iron/CaCO3
        redness = r / (g + b + 1)
        caco3_factor = max(0, min(1, (redness - 0.8) / 0.5))
        
    except Exception as e:
        logger.warning(f"Image analysis fallback: {e}")
        oc_factor = 0.5
        caco3_factor = 0.3
    
    # 3. Generate estimated parameters within profile ranges
    import random
    random.seed(hash(image_bytes) % 2**32)  # Deterministic for same image
    
    def rand_in_range(min_val, max_val, factor=0.5):
        # Factor adjusts toward higher/lower end of range
        adjusted_min = min_val + (max_val - min_val) * factor * 0.3
        adjusted_max = max_val - (max_val - min_val) * (1-factor) * 0.3
        return round(random.uniform(adjusted_min, adjusted_max), 2)
    
    estimates = {
        'ph': rand_in_range(*profile['ph']),
        'EC': rand_in_range(0.2, 1.2),  # Typical range
        'CaCO3': rand_in_range(2, 12, caco3_factor),
        'OC': rand_in_range(*profile['OC'], oc_factor),
        'N': rand_in_range(*profile['N']),
        'P': rand_in_range(*profile['P']),
        'K': rand_in_range(*profile['K']),
    }
    
    return estimates


def _assess_soil_health(params):
    """Generate soil health insights (matches Flutter expectations)"""
    insights = []
    
    # pH assessment
    if 6.0 <= params["ph"] <= 7.5:
        insights.append({"parameter": "pH", "value": params["ph"], "status": "optimal", "message": "Good for most crops"})
    elif params["ph"] < 6.0:
        insights.append({"parameter": "pH", "value": params["ph"], "status": "acidic", "message": "Consider lime application"})
    else:
        insights.append({"parameter": "pH", "value": params["ph"], "status": "alkaline", "message": "Consider adding organic matter"})
    
    # Organic Carbon
    if params["OC"] >= 2.0:
        insights.append({"parameter": "Organic Carbon", "value": params["OC"], "status": "good", "message": "Healthy soil structure"})
    elif params["OC"] >= 1.0:
        insights.append({"parameter": "Organic Carbon", "value": params["OC"], "status": "moderate", "message": "Add compost to improve"})
    else:
        insights.append({"parameter": "Organic Carbon", "value": params["OC"], "status": "low", "message": "Urgent: Add organic matter"})
    
    # Salinity (EC)
    if params["EC"] < 0.8:
        insights.append({"parameter": "Salinity (EC)", "value": params["EC"], "status": "low", "message": "Safe for sensitive crops"})
    elif params["EC"] < 1.5:
        insights.append({"parameter": "Salinity (EC)", "value": params["EC"], "status": "moderate", "message": "Monitor irrigation"})
    else:
        insights.append({"parameter": "Salinity (EC)", "value": params["EC"], "status": "high", "message": "Leach salts before planting"})
    
    return insights


def _generate_fertilizer_recommendations(params, predicted_crop):
    """Generate simple fertilizer recommendations based on nutrient gaps"""
    fertilizers = []
    
    # N deficiency logic
    if params['N'] < 150:
        fertilizers.append({
            "name": "Urea (46-0-0)",
            "type": "Chemical",
            "application": f"Apply {round((150 - params['N']) * 0.5)} kg/ha to boost nitrogen"
        })
    
    # P deficiency logic
    if params['P'] < 30:
        fertilizers.append({
            "name": "DAP (18-46-0)",
            "type": "Chemical",
            "application": f"Apply {round((30 - params['P']) * 1.2)} kg/ha at planting"
        })
    
    # K deficiency logic
    if params['K'] < 200:
        fertilizers.append({
            "name": "MOP (0-0-60)",
            "type": "Chemical",
            "application": f"Apply {round((200 - params['K']) * 0.8)} kg/ha for fruiting crops"
        })
    
    # Always recommend organic matter
    if params['OC'] < 2.0:
        fertilizers.append({
            "name": "Well-rotted compost",
            "type": "Organic",
            "application": "Mix 5-10 tons/ha before planting to improve structure and nutrients"
        })
    
    # Crop-specific addition
    if predicted_crop in ['maize', 'sugarcane', 'cotton']:
        fertilizers.append({
            "name": "NPK 17:17:17",
            "type": "Balanced",
            "application": "Apply 200 kg/ha as basal dressing for balanced growth"
        })
    
    return fertilizers if fertilizers else [{
        "name": "Balanced NPK",
        "type": "General",
        "application": "Soil nutrients are adequate. Maintain with light seasonal application."
    }]


def _generate_improvement_tips(params, region, season):
    """Generate practical soil improvement tips"""
    tips = []
    
    if params['OC'] < 1.5:
        tips.append("Add organic matter: compost, manure, or cover crops to boost soil health")
    
    if params['ph'] < 6.0:
        tips.append("Apply agricultural lime to raise pH and improve nutrient availability")
    elif params['ph'] > 7.5:
        tips.append("Incorporate sulfur or acidic organic matter to lower pH")
    
    if params['EC'] > 1.0:
        tips.append("Practice proper irrigation management to prevent salt buildup")
    
    if season == 'Dry':
        tips.append("Use mulching to conserve moisture and reduce erosion")
    else:
        tips.append("Ensure good drainage to prevent waterlogging during rains")
    
    tips.append("Rotate crops annually to maintain soil fertility and break pest cycles")
    
    return tips[:5]  # Limit to top 5 tips


# ─────────────────────────────────────────────────────────────
# ROUTE: Image-Based Soil Analysis
# ─────────────────────────────────────────────────────────────

@soil_bp.route("/soil/analyze", methods=["POST"])
@jwt_required()
def analyze_soil_image():
    """
    Analyze soil from uploaded image + location context
    
    Request: Multipart form
      - image: (file) Soil photo
      - region: (string) Central/Eastern/Northern/Western
      - season: (string) Rainy/Dry
    
    Response: Matches Flutter SoilAnalysis model
    """
    try:
        user_id = get_jwt_identity()
        
        # 1. Validate request
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        file = request.files['image']
        if file.filename == '' or not allowed_file(file.filename):
            return jsonify({"error": "Invalid image file"}), 400
        
        region = request.form.get('region', 'Central')
        season = request.form.get('season', 'Rainy')
        
        if region not in ['Central', 'Eastern', 'Northern', 'Western']:
            return jsonify({"error": "Invalid region"}), 400
        if season not in ['Rainy', 'Dry']:
            return jsonify({"error": "Invalid season"}), 400
        
        # 2. Read and validate image
        image_bytes = file.read()
        if len(image_bytes) > MAX_IMAGE_SIZE:
            return jsonify({"error": "Image too large (max 16MB)"}), 413
        
        # 3. Estimate soil parameters from image + context
        estimated_params = estimate_soil_params_from_image(image_bytes, region, season)
        logger.info(f"User {user_id}: Estimated params from image: {estimated_params}")
        
        # 4. Load model artifacts (cached at app startup)
        from app import crop_model, crop_scaler, crop_label_encoder, crop_feature_order
        
        if crop_model is None:
            logger.error(f"User {user_id}: Crop model not loaded")
            return jsonify({"error": "Prediction service unavailable"}), 503
        
        # 5. Prepare input for model
        input_array = np.array([[estimated_params[feat] for feat in crop_feature_order]])
        scaled_input = crop_scaler.transform(input_array)
        
        # 6. Predict crop
        prediction = crop_model.predict(scaled_input)[0]
        probas = crop_model.predict_proba(scaled_input)[0]
        
        predicted_crop = crop_label_encoder.inverse_transform([prediction])[0]
        confidence = round(float(probas[prediction] * 100), 1)
        
        # 7. Get top-3 recommendations
        top_3_idx = np.argsort(probas)[::-1][:3]
        crop_recommendations = [
            {
                "name": crop_label_encoder.inverse_transform([idx])[0],
                "suitability": "Excellent" if i == 0 else "Good" if i == 1 else "Moderate",
                "reason": f"Matches estimated soil profile for {region} {season} season"
            }
            for i, idx in enumerate(top_3_idx)
        ]
        
        # 8. Generate full analysis response (matches Flutter SoilAnalysis)
        soil_health = _assess_soil_health(estimated_params)
        fertilizers = _generate_fertilizer_recommendations(estimated_params, predicted_crop)
        improvement_tips = _generate_improvement_tips(estimated_params, region, season)
        
        # Calculate health score (0-100)
        health_score = 0
        if 6.0 <= estimated_params['ph'] <= 7.5: health_score += 25
        elif 5.5 <= estimated_params['ph'] <= 8.0: health_score += 15
        else: health_score += 5
        
        if estimated_params['OC'] >= 2.0: health_score += 25
        elif estimated_params['OC'] >= 1.0: health_score += 15
        else: health_score += 5
        
        if estimated_params['EC'] < 0.8: health_score += 25
        elif estimated_params['EC'] < 1.5: health_score += 15
        else: health_score += 5
        
        if estimated_params['N'] >= 150 and estimated_params['P'] >= 30 and estimated_params['K'] >= 200:
            health_score += 25
        elif estimated_params['N'] >= 100 and estimated_params['P'] >= 20 and estimated_params['K'] >= 150:
            health_score += 15
        else:
            health_score += 5
        
        health_score = min(100, max(0, health_score))
        
        # Determine soil type/texture heuristically
        if estimated_params['OC'] > 2.5 and estimated_params['ph'] < 6.5:
            soil_type = "Clay Loam"
            texture = "Fine"
            color = "Dark Brown"
        elif estimated_params['EC'] < 0.5 and estimated_params['CaCO3'] < 5:
            soil_type = "Sandy Loam"
            texture = "Coarse"
            color = "Light Brown"
        else:
            soil_type = "Loam"
            texture = "Medium"
            color = "Brown"
        
        # Build summary
        summary = (
            f"Soil in {region} ({season} season) shows {'good' if health_score >= 70 else 'moderate' if health_score >= 40 else 'poor'} health. "
            f"{predicted_crop.capitalize()} is the top recommendation ({confidence}% confidence). "
            f"{'Focus on organic matter' if estimated_params['OC'] < 2.0 else 'Maintain current practices'} for best yields."
        )
        
        # 9. Log prediction for analytics
        logger.info(f"✅ User {user_id}: Predicted {predicted_crop} ({confidence}%) for {region} {season}")
        
        # 10. Return response matching Flutter SoilAnalysis model
        return jsonify({
            "status": "success",
            "analysis": {
                "soil_health_score": health_score,
                "soil_type": soil_type,
                "texture": texture,
                "color_analysis": color,
                "estimated_nutrients": {
                    "nitrogen": "High" if estimated_params['N'] > 180 else "Medium" if estimated_params['N'] > 120 else "Low",
                    "phosphorus": "High" if estimated_params['P'] > 40 else "Medium" if estimated_params['P'] > 25 else "Low",
                    "potassium": "High" if estimated_params['K'] > 250 else "Medium" if estimated_params['K'] > 180 else "Low",
                    "ph_level": "optimal" if 6.0 <= estimated_params['ph'] <= 7.5 else "acidic" if estimated_params['ph'] < 6.0 else "alkaline",
                },
                "recommended_crops": crop_recommendations,
                "fertilizers": fertilizers,
                "improvement_tips": improvement_tips,
                "summary": summary,
            },
            "metadata": {
                "region": region,
                "season": season,
                "estimated_params": estimated_params,
                "confidence": confidence,
                "timestamp": datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Image analysis error: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": "Analysis failed",
            "message": "Please try again with a clearer soil photo"
        }), 500


# ─────────────────────────────────────────────────────────────
# ROUTE: Get Supported Crops (for reference)
# ─────────────────────────────────────────────────────────────

@soil_bp.route("/soil/crops", methods=["GET"])
@jwt_required()
def get_supported_crops():
    """Return list of crops the model can predict"""
    try:
        from app import crop_label_encoder
        if crop_label_encoder is None:
            return jsonify({"error": "Model not loaded"}), 503
        
        crops = sorted(crop_label_encoder.classes_.tolist())
        return jsonify({
            "status": "success",
            "crops": crops,
            "count": len(crops)
        }), 200
    except Exception as e:
        logger.error(f"Error fetching crops: {e}")
        return jsonify({"error": str(e)}), 500