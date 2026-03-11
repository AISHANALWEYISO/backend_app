from flask import Flask, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os

load_dotenv()

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-key')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/yucca_agro'
    )

    db.init_app(app)
    jwt.init_app(app)

    from app.controllers.user.auth_controller import auth_bp
    from app.controllers.disease_controller import disease_bp
    from app.controllers.tips.tips_controller import tips_bp
    from routes.weather_route import weather_bp
    from routes.soilscanner_route import soil_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(tips_bp, url_prefix="/api")
    app.register_blueprint(disease_bp, url_prefix="/api")
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(soil_bp, url_prefix="/api")

    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            res = make_response('', 200)
            res.headers.remove('Access-Control-Allow-Origin')
            res.headers['Access-Control-Allow-Origin'] = '*'
            res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            return res

    @app.after_request
    def add_cors(response):
        response.headers.remove('Access-Control-Allow-Origin')
        response.headers.remove('Access-Control-Allow-Headers')
        response.headers.remove('Access-Control-Allow-Methods')
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        return response

    with app.app_context():
        db.create_all()

    return app