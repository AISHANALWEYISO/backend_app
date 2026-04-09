# import os
# import uuid
# from flask import Blueprint, request, jsonify
# from sqlalchemy import select
# from sqlalchemy.exc import SQLAlchemyError
# from flask_jwt_extended import jwt_required
# from app.extensions import db
# from app.models.disease import Disease

# disease_bp = Blueprint('diseases', __name__)

# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# UPLOAD_FOLDER = 'static/uploads/diseases'

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# @disease_bp.route('/', methods=['GET'])
# def get_all_diseases():
#     try:
#         search = request.args.get('search')
#         stmt = select(Disease)
        
#         if search:
#             query = f'%{search}%'
#             stmt = stmt.where(
#                 Disease.name.ilike(query) | 
#                 Disease.description.ilike(query)
#             )
            
#         stmt = stmt.order_by(Disease.name.asc())
#         diseases = db.session.scalars(stmt).all()
        
#         return jsonify({'success': True, 'data': [d.to_dict() for d in diseases]}), 200
#     except Exception as e:
#         return jsonify({'success': False, 'message': 'Failed to fetch diseases', 'error': str(e)}), 500

# @disease_bp.route('/disease/<int:disease_id>', methods=['GET'])
# def get_disease(disease_id):
#     try:
#         disease = db.session.get(Disease, disease_id)
#         if not disease:
#             return jsonify({'success': False, 'message': 'Disease not found'}), 404
#         return jsonify({'success': True, 'data': disease.to_dict()}), 200
#     except Exception as e:
#         return jsonify({'success': False, 'message': 'Failed to fetch disease', 'error': str(e)}), 500

# @disease_bp.route('/create', methods=['POST'])
# @jwt_required()
# def create_disease():
#     try:
#         if request.files:
#             name = request.form.get('name', '').strip()
#             if not name:
#                 return jsonify({'success': False, 'message': 'Disease name is required'}), 400

#             image_url = None
#             file = request.files.get('image')
#             if file and file.filename and allowed_file(file.filename):
#                 ext = file.filename.rsplit('.', 1)[1].lower()
#                 filename = f"{uuid.uuid4().hex}.{ext}"
#                 os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#                 file.save(os.path.join(UPLOAD_FOLDER, filename))
#                 image_url = f"/static/uploads/diseases/{filename}"

#             disease = Disease(
#                 name=name,
#                 description=request.form.get('description', '').strip(),
#                 signs=request.form.get('signs', '').strip(),
#                 prevention=request.form.get('prevention', '').strip(),
#                 treatment=request.form.get('treatment', '').strip(),
#                 image=image_url
#             )
#         else:
#             data = request.get_json()
#             if not data:
#                 return jsonify({'success': False, 'message': 'Request body must be JSON'}), 400
                
#             name = data.get('name', '').strip()
#             if not name:
#                 return jsonify({'success': False, 'message': 'Disease name is required'}), 400

#             disease = Disease(
#                 name=name,
#                 description=data.get('description', '').strip(),
#                 signs=data.get('signs', '').strip(),
#                 prevention=data.get('prevention', '').strip(),
#                 treatment=data.get('treatment', '').strip(),
#                 image=data.get('image_url')
#             )
            
#         db.session.add(disease)
#         db.session.commit()
        
#         return jsonify({'success': True, 'message': 'Disease created', 'data': disease.to_dict()}), 201
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

# @disease_bp.route('/edit/<int:disease_id>', methods=['PUT'])
# @jwt_required()
# def update_disease(disease_id):
#     try:
#         disease = db.session.get(Disease, disease_id)
#         if not disease:
#             return jsonify({'success': False, 'message': 'Disease not found'}), 404

#         if request.files:
#             file = request.files.get('image')
#             if file and file.filename and allowed_file(file.filename):
#                 if disease.image:
#                     old_name = disease.image.split('/')[-1]
#                     old_path = os.path.join(UPLOAD_FOLDER, old_name)
#                     if os.path.exists(old_path): os.remove(old_path)
                    
#                 ext = file.filename.rsplit('.', 1)[1].lower()
#                 filename = f"{uuid.uuid4().hex}.{ext}"
#                 os.makedirs(UPLOAD_FOLDER, exist_ok=True)
#                 file.save(os.path.join(UPLOAD_FOLDER, filename))
#                 disease.image = f"/static/uploads/diseases/{filename}"
                
#             if 'name' in request.form: disease.name = request.form['name'].strip()
#             if 'description' in request.form: disease.description = request.form['description'].strip()
#             if 'signs' in request.form: disease.signs = request.form['signs'].strip()
#             if 'prevention' in request.form: disease.prevention = request.form['prevention'].strip()
#             if 'treatment' in request.form: disease.treatment = request.form['treatment'].strip()
#         else:
#             data = request.get_json()
#             if not data:
#                 return jsonify({'success': False, 'message': 'No update data provided'}), 400
                
#             if 'name' in data: disease.name = data['name'].strip()
#             if 'description' in data: disease.description = data['description'].strip()
#             if 'signs' in data: disease.signs = data['signs'].strip()
#             if 'prevention' in data: disease.prevention = data['prevention'].strip()
#             if 'treatment' in data: disease.treatment = data['treatment'].strip()
#             if 'image_url' in data: disease.image = data['image_url']

#         db.session.commit()
#         return jsonify({'success': True, 'message': 'Disease updated', 'data': disease.to_dict()}), 200
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

# @disease_bp.route('/delete/<int:disease_id>', methods=['DELETE'])
# @jwt_required()
# def delete_disease(disease_id):
#     try:
#         disease = db.session.get(Disease, disease_id)
#         if not disease:
#             return jsonify({'success': False, 'message': 'Disease not found'}), 404

#         if disease.image:
#             img_name = disease.image.split('/')[-1]
#             img_path = os.path.join(UPLOAD_FOLDER, img_name)
#             if os.path.exists(img_path): os.remove(img_path)

#         db.session.delete(disease)
#         db.session.commit()
#         return jsonify({'success': True, 'message': 'Disease deleted'}), 200
#     except SQLAlchemyError as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

import os
import uuid
from flask import Blueprint, request, jsonify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.disease import Disease

disease_bp = Blueprint('diseases', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads/diseases'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ✅ GET all diseases: /api/diseases/
@disease_bp.route('/', methods=['GET'])
def get_all_diseases():
    try:
        search = request.args.get('search')
        stmt = select(Disease)
        
        if search:
            query = f'%{search}%'
            stmt = stmt.where(
                Disease.name.ilike(query) | 
                Disease.description.ilike(query)
            )
        stmt = stmt.order_by(Disease.name.asc())
        diseases = db.session.scalars(stmt).all()
        return jsonify({'success': True, 'data': [d.to_dict() for d in diseases]}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch diseases', 'error': str(e)}), 500

# ✅ GET single disease: /api/diseases/1
@disease_bp.route('/<int:disease_id>', methods=['GET'])
def get_disease(disease_id):
    try:
        disease = db.session.get(Disease, disease_id)
        if not disease:
            return jsonify({'success': False, 'message': 'Disease not found'}), 404
        return jsonify({'success': True, 'data': disease.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch disease', 'error': str(e)}), 500

# ✅ CREATE disease: POST /api/diseases/
@disease_bp.route('/', methods=['POST'])
@jwt_required()
def create_disease():
    try:
        if request.files:
            name = request.form.get('name', '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Disease name is required'}), 400

            image_url = None
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_url = f"/static/uploads/diseases/{filename}"

            disease = Disease(
                name=name,
                description=request.form.get('description', '').strip(),
                signs=request.form.get('signs', '').strip(),
                prevention=request.form.get('prevention', '').strip(),
                treatment=request.form.get('treatment', '').strip(),
                image=image_url
            )
        else:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Request body must be JSON'}), 400
                
            name = data.get('name', '').strip()
            if not name:
                return jsonify({'success': False, 'message': 'Disease name is required'}), 400

            disease = Disease(
                name=name,
                description=data.get('description', '').strip(),
                signs=data.get('signs', '').strip(),
                prevention=data.get('prevention', '').strip(),
                treatment=data.get('treatment', '').strip(),
                image=data.get('image_url')
            )
            
        db.session.add(disease)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Disease created', 'data': disease.to_dict()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

# ✅ UPDATE disease: PUT /api/diseases/1
@disease_bp.route('/<int:disease_id>', methods=['PUT'])
@jwt_required()
def update_disease(disease_id):
    try:
        disease = db.session.get(Disease, disease_id)
        if not disease:
            return jsonify({'success': False, 'message': 'Disease not found'}), 404

        if request.files:
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                if disease.image:
                    old_name = disease.image.split('/')[-1]
                    old_path = os.path.join(UPLOAD_FOLDER, old_name)
                    if os.path.exists(old_path): os.remove(old_path)
                    
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                disease.image = f"/static/uploads/diseases/{filename}"
                
            if 'name' in request.form: disease.name = request.form['name'].strip()
            if 'description' in request.form: disease.description = request.form['description'].strip()
            if 'signs' in request.form: disease.signs = request.form['signs'].strip()
            if 'prevention' in request.form: disease.prevention = request.form['prevention'].strip()
            if 'treatment' in request.form: disease.treatment = request.form['treatment'].strip()
        else:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No update data provided'}), 400
                
            if 'name' in data: disease.name = data['name'].strip()
            if 'description' in data: disease.description = data['description'].strip()
            if 'signs' in data: disease.signs = data['signs'].strip()
            if 'prevention' in data: disease.prevention = data['prevention'].strip()
            if 'treatment' in data: disease.treatment = data['treatment'].strip()
            if 'image_url' in data: disease.image = data['image_url']

        db.session.commit()
        return jsonify({'success': True, 'message': 'Disease updated', 'data': disease.to_dict()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

# ✅ DELETE disease: DELETE /api/diseases/1
@disease_bp.route('/<int:disease_id>', methods=['DELETE'])
@jwt_required()
def delete_disease(disease_id):
    try:
        disease = db.session.get(Disease, disease_id)
        if not disease:
            return jsonify({'success': False, 'message': 'Disease not found'}), 404

        if disease.image:
            img_name = disease.image.split('/')[-1]
            img_path = os.path.join(UPLOAD_FOLDER, img_name)
            if os.path.exists(img_path): os.remove(img_path)

        db.session.delete(disease)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Disease deleted'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500