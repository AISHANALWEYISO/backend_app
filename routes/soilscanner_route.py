from flask import Blueprint
from app.controllers.soilscanner_controller import scan_soil

soil_bp = Blueprint("soil", __name__)

# POST /api/soil/analyze
soil_bp.route("/soil/analyze", methods=["POST"])(scan_soil)