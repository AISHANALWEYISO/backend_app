
# from flask import Flask
# from flask_migrate import Migrate
# from flask_sqlalchemy import SQLAlchemy
# from flask_jwt_extended import JWTManager
# from flask_cors import CORS
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # ── Extension instances (created once, bound to app in create_app) ──────────
# db = SQLAlchemy()
# jwt = JWTManager()
# migrate = Migrate()


# def create_app():
#     app = Flask(__name__)

#     # ── Configuration ────────────────────────────────────────────────────────
#     app.config['SECRET_KEY']                  = os.getenv('SECRET_KEY', 'dev-secret-key')
#     app.config['JWT_SECRET_KEY']              = os.getenv('JWT_SECRET_KEY', 'dev-jwt-key')
#     app.config['SQLALCHEMY_DATABASE_URI']     = os.getenv(
#         'DATABASE_URL',
#         'mysql+pymysql://root:@localhost/yucca_agro'
#     )
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # ── Extensions ───────────────────────────────────────────────────────────
#     db.init_app(app)
#     jwt.init_app(app)
#     migrate.init_app(app, db)

#     # ── CORS ─────────────────────────────────────────────────────────────────
#     # origins="*" works cleanly without supports_credentials.
#     # For production, replace "*" with your exact frontend URL.
#     CORS(
#         app,
#         resources={r"/api/*": {"origins": "*"}},
#         allow_headers=["Content-Type", "Authorization"],
#         methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
#     )

#     # ── Blueprints ───────────────────────────────────────────────────────────
#     from app.controllers.user.auth_controller import auth_bp
#     from app.controllers.disease_controller   import disease_bp
#     from app.controllers.tips.tips_controller import tips_bp
#     from app.controllers.payment_controller   import payment_bp
#     from app.controllers.user_controller      import user_bp
#     from routes.weather_route                 import weather_bp
#     from routes.soilscanner_route             import soil_bp

#     app.register_blueprint(auth_bp,    url_prefix="/api/auth")
#     app.register_blueprint(tips_bp,    url_prefix="/api")
#     app.register_blueprint(disease_bp, url_prefix="/api")
#     app.register_blueprint(weather_bp, url_prefix="/api")
#     app.register_blueprint(soil_bp,    url_prefix="/api")
#     app.register_blueprint(payment_bp, url_prefix="/api/payment")
#     app.register_blueprint(user_bp,    url_prefix="/api/user")

#     return app

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()

# ── Extension instances ───────────────────────────────────────────────────────
db       = SQLAlchemy()
jwt      = JWTManager()
migrate  = Migrate()


def create_app():
    app = Flask(__name__)

    # ── Configuration ─────────────────────────────────────────────────────────
    app.config['SECRET_KEY']                     = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['JWT_SECRET_KEY']                 = os.getenv('JWT_SECRET_KEY', 'dev-jwt-key')
    app.config['SQLALCHEMY_DATABASE_URI']        = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:@localhost/yucca_app'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Mail Configuration (Gmail) ────────────────────────────────────────────
    app.config['GMAIL_USER']         = os.getenv('GMAIL_USER')
    app.config['GMAIL_APP_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')

    # ── Mobile Money Numbers ──────────────────────────────────────────────────
    app.config['MTN_NUMBER']         = os.getenv('MTN_NUMBER',    '0766753527')
    app.config['AIRTEL_NUMBER']      = os.getenv('AIRTEL_NUMBER', '0750163604')

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # ── Blueprints ────────────────────────────────────────────────────────────
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