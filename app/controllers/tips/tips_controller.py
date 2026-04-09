import os
import uuid
from flask import Blueprint, request, jsonify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.tips import Tip

tips_bp = Blueprint('tips', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads/tips'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@tips_bp.route('/', methods=['GET'])
def get_all_tips():
    try:
        category = request.args.get('category')
        stmt = select(Tip)
        
        if category and category.lower() != 'all':
            stmt = stmt.where(Tip.category == category)
            
        stmt = stmt.order_by(Tip.created_at.desc())
        tips = db.session.scalars(stmt).all()
        
        return jsonify({'success': True, 'data': [tip.to_dict() for tip in tips]}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch tips', 'error': str(e)}), 500

@tips_bp.route('/<int:tip_id>', methods=['GET'])
def get_tip(tip_id):
    try:
        tip = db.session.get(Tip, tip_id)
        if not tip:
            return jsonify({'success': False, 'message': 'Tip not found'}), 404
        return jsonify({'success': True, 'data': tip.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch tip', 'error': str(e)}), 500

@tips_bp.route('/', methods=['POST'])
@jwt_required()
def create_tip():
    try:
        if request.files:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', 'General')
            file = request.files.get('image')
            
            if not title or not content:
                return jsonify({'success': False, 'message': 'Title and content are required'}), 400
            
            image_url = None
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                image_url = f"/static/uploads/tips/{filename}"
            
            tip = Tip(title=title, content=content, category=category, image_url=image_url)
        else:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Request body must be JSON'}), 400
                
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
            if not title or not content:
                return jsonify({'success': False, 'message': 'Title and content are required'}), 400

            tip = Tip(
                title=title,
                content=content,
                category=data.get('category', 'General'),
                image_url=data.get('image_url')
            )
        
        db.session.add(tip)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tip created successfully', 'data': tip.to_dict()}), 201
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

@tips_bp.route('/<int:tip_id>', methods=['PUT'])
@jwt_required()
def update_tip(tip_id):
    try:
        tip = db.session.get(Tip, tip_id)
        if not tip:
            return jsonify({'success': False, 'message': 'Tip not found'}), 404

        if request.files:
            file = request.files.get('image')
            title = request.form.get('title')
            content = request.form.get('content')
            category = request.form.get('category')
            
            if title: tip.title = title.strip()
            if content: tip.content = content.strip()
            if category: tip.category = category
            
            if file and file.filename and allowed_file(file.filename):
                if tip.image_url:
                    old_filename = tip.image_url.split('/')[-1]
                    old_path = os.path.join(UPLOAD_FOLDER, old_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                tip.image_url = f"/static/uploads/tips/{filename}"
        else:
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'No update data provided'}), 400

            if 'title' in data: tip.title = data['title'].strip()
            if 'content' in data: tip.content = data['content'].strip()
            if 'category' in data: tip.category = data['category']
            if 'image_url' in data: tip.image_url = data['image_url']

        db.session.commit()
        return jsonify({'success': True, 'message': 'Tip updated successfully', 'data': tip.to_dict()}), 200
        
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

@tips_bp.route('/<int:tip_id>', methods=['DELETE'])
@jwt_required()
def delete_tip(tip_id):
    try:
        tip = db.session.get(Tip, tip_id)
        if not tip:
            return jsonify({'success': False, 'message': 'Tip not found'}), 404

        if tip.image_url:
            old_filename = tip.image_url.split('/')[-1]
            image_path = os.path.join(UPLOAD_FOLDER, old_filename)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(tip)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Tip deleted successfully'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500