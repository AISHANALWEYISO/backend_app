from flask import Blueprint, jsonify , request
from app.models.disease import Disease
from app import db
from flask_jwt_extended import create_access_token , get_jwt_identity, jwt_required

disease_bp = Blueprint('disease', __name__)


# Create a new disease
@disease_bp.route('/diseases', methods=['POST'])
@jwt_required()  
def create_disease():
    data = request.get_json()

    # Get fields from request
    name = data.get('name')
    description = data.get('description')
    signs = data.get('signs')
    prevention = data.get('prevention')
    treatment = data.get('treatment')
    image = data.get('image')

    # Validation
    if not name:
        return jsonify({"message": "Name is required"}), 400

    if Disease.query.filter_by(name=name).first():
        return jsonify({"message": "Disease already exists"}), 400

    # Create disease object
    disease = Disease(
        name=name,
        description=description,
        signs=signs,
        prevention=prevention,
        treatment=treatment,
        image=image
    )

    # Save to DB
    db.session.add(disease)
    db.session.commit()

    # Return response
    return jsonify({
        "message": "Disease created successfully",
        "disease": {
            "id": disease.id,
            "name": disease.name,
            "description": disease.description,
            "signs": disease.signs,
            "prevention": disease.prevention,
            "treatment": disease.treatment,
            "image": disease.image
        }
    }), 201

# get all diseases
@disease_bp.route('/diseases', methods=['GET'])
def get_diseases():
    diseases = Disease.query.all()

    result = []
    for d in diseases:
        result.append({
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "signs": d.signs,
            "prevention": d.prevention,
            "treatment": d.treatment,
            "image": d.image
        })

    return jsonify(result)

## updating the disease

@disease_bp.route('/diseases/<int:id>', methods=['PUT'])
@jwt_required()  # optional, use if you want JWT protection
def update_disease(id):
    disease = Disease.query.get_or_404(id)
    data = request.get_json()

    # Update fields if provided, otherwise keep existing values
    disease.name = data.get('name', disease.name)
    disease.description = data.get('description', disease.description)
    disease.signs = data.get('signs', disease.signs)
    disease.prevention = data.get('prevention', disease.prevention)
    disease.treatment = data.get('treatment', disease.treatment)
    disease.image = data.get('image', disease.image)

    db.session.commit()

    return jsonify({
        "message": "Disease updated successfully",
        "disease": {
            "id": disease.id,
            "name": disease.name,
            "description": disease.description,
            "signs": disease.signs,
            "prevention": disease.prevention,
            "treatment": disease.treatment,
            "image": disease.image
        }
    }), 200

## deleting the disease

@disease_bp.route('/diseases/<int:id>', methods=['DELETE'])
@jwt_required()  # optional
def delete_disease(id):
    disease = Disease.query.get_or_404(id)

    db.session.delete(disease)
    db.session.commit()

    return jsonify({"message": "Disease deleted successfully"}), 200