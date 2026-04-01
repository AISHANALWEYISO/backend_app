

# from flask import Flask, request, make_response
# from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os

# load_dotenv()

# db = SQLAlchemy()
# jwt = JWTManager()
# migrate = Migrate() 

# def create_app():
#     app = Flask(__name__)
    
#     # Enable CORS
#     CORS(app, resources={r"/api/*": {"origins": "*"}})
    
#     app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
#     app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-key')
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#     app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
#         'DATABASE_URL',
#         'mysql+pymysql://root:@localhost/yucca_agro'
#     )
    
#     db.init_app(app)
#     jwt.init_app(app)
#     migrate.init_app(app, db)

#     # Register blueprints
#     from app.controllers.user.auth_controller import auth_bp
#     from app.controllers.disease_controller import disease_bp
#     from app.controllers.tips.tips_controller import tips_bp
#     from routes.weather_route import weather_bp
#     from routes.soilscanner_route import soil_bp
#     from app.controllers.payment_controller import payment_bp
#     from app.controllers.user_controller import user_bp

    
#     app.register_blueprint(auth_bp, url_prefix="/api/auth")
#     app.register_blueprint(tips_bp, url_prefix="/api")
#     app.register_blueprint(disease_bp, url_prefix="/api")
#     app.register_blueprint(weather_bp, url_prefix="/api")
#     app.register_blueprint(soil_bp, url_prefix="/api")
#     app.register_blueprint(payment_bp, url_prefix = '/api/payment')
#     app.register_blueprint(user_bp, url_prefix='/api/user')
    
#     @app.before_request
#     def handle_preflight():
#         if request.method == 'OPTIONS':
#             res = make_response('', 200)
#             res.headers.remove('Access-Control-Allow-Origin')
#             res.headers['Access-Control-Allow-Origin'] = '*'
#             res.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
#             res.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
#             return res
    
#     @app.after_request
#     def add_cors(response):
#         response.headers.remove('Access-Control-Allow-Origin')
#         response.headers.remove('Access-Control-Allow-Headers')
#         response.headers.remove('Access-Control-Allow-Methods')
#         response.headers['Access-Control-Allow-Origin'] = '*'
#         response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
#         response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
#         return response
    
#     with app.app_context():
#         db.create_all()
    
#     return app

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

# ── Extension instances (created once, bound to app in create_app) ──────────
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    # ── Configuration ────────────────────────────────────────────────────────
    app.config['SECRET_KEY']                  = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY']              = os.getenv('JWT_SECRET_KEY', 'dev-jwt-key')
    app.config['SQLALCHEMY_DATABASE_URI']     = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/yucca_agro'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Extensions ───────────────────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ── CORS ─────────────────────────────────────────────────────────────────
    # origins="*" works cleanly without supports_credentials.
    # For production, replace "*" with your exact frontend URL.
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # ── Blueprints ───────────────────────────────────────────────────────────
    from app.controllers.user.auth_controller import auth_bp
    from app.controllers.disease_controller   import disease_bp
    from app.controllers.tips.tips_controller import tips_bp
    from app.controllers.payment_controller   import payment_bp
    from app.controllers.user_controller      import user_bp
    from routes.weather_route                 import weather_bp
    from routes.soilscanner_route             import soil_bp

    app.register_blueprint(auth_bp,    url_prefix="/api/auth")
    app.register_blueprint(tips_bp,    url_prefix="/api")
    app.register_blueprint(disease_bp, url_prefix="/api")
    app.register_blueprint(weather_bp, url_prefix="/api")
    app.register_blueprint(soil_bp,    url_prefix="/api")
    app.register_blueprint(payment_bp, url_prefix="/api/payment")
    app.register_blueprint(user_bp,    url_prefix="/api/user")

    return app