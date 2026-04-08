# from flask import Blueprint, request, jsonify
# from app.models.tips import db, Tip
# from functools import wraps

# tips_bp = Blueprint('tips', __name__, url_prefix='/api/tips')

# # ✅ GET ALL TIPS (Public - Mobile App)
# @tips_bp.route('/', methods=['GET'])
# def get_all_tips():
#     try:
#         category = request.args.get('category')
#         query = Tip.query.filter_by(is_published=True)
        
#         if category:
#             query = query.filter_by(category=category)
        
#         tips = query.order_by(Tip.created_at.desc()).all()
#         return jsonify({
#             'success': True,
#             'data': [tip.to_dict() for tip in tips]
#         }), 200
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500

# # ✅ GET SINGLE TIP (Public - Mobile App)
# @tips_bp.route('/<int:tip_id>', methods=['GET'])
# def get_tip(tip_id):
#     try:
#         tip = Tip.query.get_or_404(tip_id)
#         return jsonify({
#             'success': True,
#             'data': tip.to_dict()
#         }), 200
#     except Exception as e:
#         return jsonify({'success': False, 'message': str(e)}), 500

# # ─────────────────────────────────────────
# # ⚠️ ADMIN ONLY ROUTES (Web Dashboard)
# # ─────────────────────────────────────────

# def require_admin(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.headers.get('Authorization')
#         if not token or not token.startswith('Bearer '):
#             return jsonify({'success': False, 'message': 'Unauthorized'}), 401
#         # Verify admin token here
#         return f(*args, **kwargs)
#     return decorated

# # ✅ CREATE TIP (Admin Dashboard Only)
# @tips_bp.route('/', methods=['POST'])
# @require_admin
# def create_tip():
#     try:
#         data = request.get_json()
        
#         if not data.get('title') or not data.get('content'):
#             return jsonify({'success': False, 'message': 'Title and content required'}), 400
        
#         tip = Tip(
#             title=data['title'],
#             content=data['content'],
#             category=data.get('category', 'General'),
#             image_url=data.get('image_url'),
#             is_published=data.get('is_published', True),
#             created_by=data.get('created_by')
#         )
        
#         db.session.add(tip)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Tip created successfully',
#             'data': tip.to_dict()
#         }), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500

# # ✅ UPDATE TIP (Admin Dashboard Only)
# @tips_bp.route('/<int:tip_id>', methods=['PUT'])
# @require_admin
# def update_tip(tip_id):
#     try:
#         tip = Tip.query.get_or_404(tip_id)
#         data = request.get_json()
        
#         tip.title = data.get('title', tip.title)
#         tip.content = data.get('content', tip.content)
#         tip.category = data.get('category', tip.category)
#         tip.image_url = data.get('image_url', tip.image_url)
#         tip.is_published = data.get('is_published', tip.is_published)
        
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Tip updated successfully',
#             'data': tip.to_dict()
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500

# # ✅ DELETE TIP (Admin Dashboard Only)
# @tips_bp.route('/<int:tip_id>', methods=['DELETE'])
# @require_admin
# def delete_tip(tip_id):
#     try:
#         tip = Tip.query.get_or_404(tip_id)
#         db.session.delete(tip)
#         db.session.commit()
        
#         return jsonify({
#             'success': True,
#             'message': 'Tip deleted successfully'
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500

from flask import Blueprint, request, jsonify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from app.models.tips import db, Tip

tips_bp = Blueprint('tips', __name__)


def admin_jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            
            # Adjust based on how you structure your JWT payload
            # Accepts either `is_admin: true` or `role: "admin"`
            if not (claims.get('is_admin') is True or claims.get('role') == 'admin'):
                return jsonify({'success': False, 'message': 'Admin privileges required'}), 403
                
            return f(*args, **kwargs)
        except Exception:
            return jsonify({'success': False, 'message': 'Invalid, expired, or missing JWT token'}), 401
    return wrapper

# ─────────────────────────────────────────
# 
# ─────────────────────────────────────────

@tips_bp.route('/', methods=['GET'])
def get_all_tips():
    try:
        stmt = select(Tip).order_by(Tip.created_at.desc())
        tips = db.session.scalars(stmt).all()
        
        return jsonify({
            'success': True,
            'data': [tip.to_dict() for tip in tips]
        }), 200
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

# ─────────────────────────────────────────
# 🛡️ PROTECTED ROUTES (JWT + Admin Only)
# ─────────────────────────────────────────

@tips_bp.route('/', methods=['POST'])
@admin_jwt_required
def create_tip():
    try:
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
            image_url=data.get('image_url')
        )
        
        db.session.add(tip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tip created successfully',
            'data': tip.to_dict()
        }), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

@tips_bp.route('/<int:tip_id>', methods=['PUT'])
@admin_jwt_required
def update_tip(tip_id):
    try:
        tip = db.session.get(Tip, tip_id)
        if not tip:
            return jsonify({'success': False, 'message': 'Tip not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No update data provided'}), 400

        if 'title' in data:
            tip.title = data['title'].strip()
        if 'content' in data:
            tip.content = data['content'].strip()
        if 'image_url' in data:
            tip.image_url = data['image_url']

        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tip updated successfully',
            'data': tip.to_dict()
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

@tips_bp.route('/<int:tip_id>', methods=['DELETE'])
@admin_jwt_required
def delete_tip(tip_id):
    try:
        tip = db.session.get(Tip, tip_id)
        if not tip:
            return jsonify({'success': False, 'message': 'Tip not found'}), 404

        db.session.delete(tip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tip deleted successfully'
        }), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500