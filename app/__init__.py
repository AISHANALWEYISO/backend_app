from flask import Flask, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import os

from app.extensions import db, jwt, migrate

load_dotenv()

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-jwt-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/yucca_app'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['GMAIL_USER'] = os.getenv('GMAIL_USER')
    app.config['GMAIL_APP_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')
    app.config['MTN_NUMBER'] = os.getenv('MTN_NUMBER', '0766753527')
    app.config['AIRTEL_NUMBER'] = os.getenv('AIRTEL_NUMBER', '0750163604')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ✅ CORS: Fixed for Flutter Web preflight + credentials
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": ["*", "http://localhost:56079", "http://127.0.0.1:56079"],
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                "supports_credentials": True,
                "expose_headers": ["Content-Type"],
            }
        },
        intercept_exceptions=True,
    )

    # Serve uploaded images
    @app.route('/static/uploads/tips/<filename>')
    def serve_tip_image(filename):
        return send_from_directory('static/uploads/tips', filename)
    
    @app.route('/static/uploads/diseases/<filename>')
    def serve_disease_image(filename):
        return send_from_directory('static/uploads/diseases', filename)

    # Import blueprints
    from app.controllers.user.auth_controller import auth_bp
    from app.controllers.disease_controller import disease_bp
    from app.controllers.tips.tips_controller import tips_bp
    from app.controllers.payment_controller import payment_bp
    from app.controllers.user_controller import user_bp
    from routes.weather_route import weather_bp
    from routes.soilscanner_route import soil_bp
    from app.controllers.market_controller import market_bp

    # ✅ Register blueprints with DEDICATED prefixes to avoid conflicts
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tips_bp, url_prefix="/api")              # Tips: /api/
    app.register_blueprint(disease_bp, url_prefix="/api/diseases")  # ✅ Diseases: /api/diseases/
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(soil_bp, url_prefix="/api")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(user_bp, url_prefix="/api/user")
    app.register_blueprint(market_bp, url_prefix = '/api/market')

    return app