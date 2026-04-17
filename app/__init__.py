

# from flask import Flask, send_from_directory
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os

# from app.extensions import db, jwt, migrate

# load_dotenv()


# def create_app():
#     app = Flask(__name__, static_folder="static", static_url_path="/static")

#     # =========================
#     # CONFIGURATION
#     # =========================
#     app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
#     app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")

#     app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
#         "DATABASE_URL",
#         "mysql+pymysql://root:@localhost/yucca_app"
#     )
#     app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

#     app.config["GMAIL_USER"] = os.getenv("GMAIL_USER")
#     app.config["GMAIL_APP_PASSWORD"] = os.getenv("GMAIL_APP_PASSWORD")

#     app.config["MTN_NUMBER"] = os.getenv("MTN_NUMBER", "0766753527")
#     app.config["AIRTEL_NUMBER"] = os.getenv("AIRTEL_NUMBER", "0750163604")

#     app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB upload limit

#     # =========================
#     # EXTENSIONS INIT
#     # =========================
#     db.init_app(app)
#     jwt.init_app(app)
#     migrate.init_app(app, db)

#     # =========================
#     # CORS CONFIGURATION (STABLE FIX)
#     # =========================
#     # Detect environment: development vs production
#     FLASK_ENV = os.getenv("FLASK_ENV", "development")
#     is_dev = FLASK_ENV == "development"

#     # For development: use wildcard to allow any Flutter dev port
#     # For production: specify your exact frontend domain(s)
#     if is_dev:
#         cors_origins = "*"
#         supports_credentials = False  # Required when using "*"
#     else:
#         cors_origins = [
#             "https://your-production-domain.com",
#             "https://www.your-production-domain.com",
#         ]
#         supports_credentials = True

#     CORS(
#         app,
#         resources={
#             r"/*": {
#                 "origins": cors_origins,
#                 "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
#                 "allow_headers": [
#                     "Content-Type",
#                     "Authorization",
#                     "X-Requested-With",
#                     "Accept",
#                 ],
#                 "supports_credentials": supports_credentials,
#                 "expose_headers": ["Content-Type", "Authorization"],
#             }
#         },
#         intercept_exceptions=True,
#     )

#     # =========================
#     # STATIC FILE ROUTES
#     # =========================
#     @app.route("/static/uploads/tips/<filename>")
#     def serve_tip_image(filename):
#         return send_from_directory("static/uploads/tips", filename)

#     @app.route("/static/uploads/diseases/<filename>")
#     def serve_disease_image(filename):
#         return send_from_directory("static/uploads/diseases", filename)

#     # =========================
#     # BLUEPRINT IMPORTS
#     # =========================
#     from app.controllers.user.auth_controller import auth_bp
#     from app.controllers.disease_controller import disease_bp
#     from app.controllers.tips.tips_controller import tips_bp
#     from app.controllers.payment_controller import payment_bp
#     from app.controllers.user_controller import user_bp
#     from routes.weather_route import weather_bp
#     from routes.soilscanner_route import soil_bp
#     from app.controllers.market_controller import market_bp

#     # =========================
#     # BLUEPRINT REGISTRATION
#     # =========================
#     app.register_blueprint(auth_bp, url_prefix="/api/auth")
#     app.register_blueprint(user_bp, url_prefix="/api/user")

#     app.register_blueprint(disease_bp, url_prefix="/api/diseases")
#     app.register_blueprint(tips_bp, url_prefix="/api")
#     app.register_blueprint(market_bp, url_prefix="/api/market")

#     app.register_blueprint(payment_bp, url_prefix="/api/payment")

#     app.register_blueprint(weather_bp, url_prefix="/api")
#     app.register_blueprint(soil_bp, url_prefix="/api")

#     return app

from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os
import joblib
from pathlib import Path
import logging

from app.extensions import db, jwt, migrate

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# ─────────────────────────────────────────────────────────────
# GLOBAL MODEL VARIABLES (Accessible via app context)
# ─────────────────────────────────────────────────────────────
crop_model = None
crop_scaler = None
crop_label_encoder = None
crop_feature_order = None


def load_crop_model():
    """Load crop prediction model artifacts at startup"""
    global crop_model, crop_scaler, crop_label_encoder, crop_feature_order
    
    try:
        model_dir = Path(__file__).parent.parent / "model_artifacts"
        
        if not model_dir.exists():
            logger.warning(f" Model directory not found: {model_dir}")
            return False
        
        crop_model = joblib.load(model_dir / "crop_model.pkl")
        crop_scaler = joblib.load(model_dir / "scaler.pkl")
        crop_label_encoder = joblib.load(model_dir / "label_encoder.pkl")
        crop_feature_order = joblib.load(model_dir / "feature_order.pkl")
        
        logger.info(" Crop prediction model loaded successfully")
        logger.info(f" Supported crops: {crop_label_encoder.classes_.tolist()}")
        return True
        
    except FileNotFoundError as e:
        logger.error(f" Model file not found: {e}")
    except Exception as e:
        logger.error(f" Failed to load crop model: {e}")
    
    return False


def create_app():
    app = Flask(__name__, static_folder="static", static_url_path="/static")

    # =========================
    # CONFIGURATION
    # =========================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost/yucca_app"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["GMAIL_USER"] = os.getenv("GMAIL_USER")
    app.config["GMAIL_APP_PASSWORD"] = os.getenv("GMAIL_APP_PASSWORD")

    app.config["MTN_NUMBER"] = os.getenv("MTN_NUMBER", "0766753527")
    app.config["AIRTEL_NUMBER"] = os.getenv("AIRTEL_NUMBER", "0750163604")

    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB upload limit

    # =========================
    # EXTENSIONS INIT
    # =========================
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # =========================
    # LOAD CROP PREDICTION MODEL
    # =========================
    with app.app_context():
        load_crop_model()

    # =========================
    # CORS CONFIGURATION
    # =========================
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    is_dev = FLASK_ENV == "development"

    if is_dev:
        cors_origins = "*"
        supports_credentials = False
    else:
        cors_origins = [
            "https://your-production-domain.com",
            "https://www.your-production-domain.com",
        ]
        supports_credentials = True

    CORS(
        app,
        resources={
            r"/*": {
                "origins": cors_origins,
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Content-Type", "Authorization", "X-Requested-With", "Accept",
                ],
                "supports_credentials": supports_credentials,
                "expose_headers": ["Content-Type", "Authorization"],
            }
        },
        intercept_exceptions=True,
    )

    # =========================
    # STATIC FILE ROUTES
    # =========================
    @app.route("/static/uploads/tips/<filename>")
    def serve_tip_image(filename):
        return send_from_directory("static/uploads/tips", filename)

    @app.route("/static/uploads/diseases/<filename>")
    def serve_disease_image(filename):
        return send_from_directory("static/uploads/diseases", filename)

    # =========================
    # HEALTH CHECK ENDPOINT
    # =========================
    @app.route("/api/health")
    def health_check():
        """API health check with model status"""
        model_status = "loaded" if crop_model is not None else "not_loaded"
        return {
            "status": "online",
            "model": "crop_prediction",
            "model_status": model_status,
            "version": "1.0.0"
        }

    # =========================
    # BLUEPRINT IMPORTS
    # =========================
    from app.controllers.user.auth_controller import auth_bp
    from app.controllers.disease_controller import disease_bp
    from app.controllers.tips.tips_controller import tips_bp
    from app.controllers.payment_controller import payment_bp
    from app.controllers.user_controller import user_bp
    from routes.weather_route import weather_bp
    from routes.soilscanner_route import soil_bp
    from app.controllers.market_controller import market_bp

    # =========================
    # BLUEPRINT REGISTRATION
    # =========================
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(disease_bp, url_prefix="/api/diseases")
    app.register_blueprint(tips_bp, url_prefix="/api")
    app.register_blueprint(market_bp, url_prefix="/api/market")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(soil_bp, url_prefix="/api")

    return app