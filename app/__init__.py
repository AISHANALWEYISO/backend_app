


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os  


load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-key')

    CORS(app, resources={
        r"/api/*": {  # Apply CORS only to /api routes
            "origins": [
                "http://localhost:64900",  # Flutter Web dev
                "http://127.0.0.1:64900",  # Alternative Flutter Web URL
                "http://localhost:*",       # Allow any localhost port (dev only)
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })

    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    # Register Blueprints
    from app.controllers.user.auth_controller import auth_bp
    from app.controllers.disease_controller import disease_bp
    from app.controllers.tips.tips_controller import tips_bp
    from routes.weather_route import weather_bp
    from routes.soilscanner_route import soil_bp

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(tips_bp, url_prefix="/api")
    app.register_blueprint(disease_bp, url_prefix="/api")
    app.register_blueprint(weather_bp, url_prefix="/api")  
    app.register_blueprint(soil_bp, url_prefix="/api") 

    with app.app_context():
        db.create_all()

    return app