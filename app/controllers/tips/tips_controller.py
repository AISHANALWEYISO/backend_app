from flask import Blueprint, request, jsonify
from app.models.tips import db, Tip
from functools import wraps

tips_bp = Blueprint('tips', __name__, url_prefix='/api/tips')

# ✅ GET ALL TIPS (Public - Mobile App)
@tips_bp.route('/', methods=['GET'])
def get_all_tips():
    try:
        category = request.args.get('category')
        query = Tip.query.filter_by(is_published=True)
        
        if category:
            query = query.filter_by(category=category)
        
        tips = query.order_by(Tip.created_at.desc()).all()
        return jsonify({
            'success': True,
            'data': [tip.to_dict() for tip in tips]
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ✅ GET SINGLE TIP (Public - Mobile App)
@tips_bp.route('/<int:tip_id>', methods=['GET'])
def get_tip(tip_id):
    try:
        tip = Tip.query.get_or_404(tip_id)
        return jsonify({
            'success': True,
            'data': tip.to_dict()
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ─────────────────────────────────────────
# ⚠️ ADMIN ONLY ROUTES (Web Dashboard)
# ─────────────────────────────────────────

def require_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        # Verify admin token here
        return f(*args, **kwargs)
    return decorated

# ✅ CREATE TIP (Admin Dashboard Only)
@tips_bp.route('/', methods=['POST'])
@require_admin
def create_tip():
    try:
        data = request.get_json()
        
        if not data.get('title') or not data.get('content'):
            return jsonify({'success': False, 'message': 'Title and content required'}), 400
        
        tip = Tip(
            title=data['title'],
            content=data['content'],
            category=data.get('category', 'General'),
            image_url=data.get('image_url'),
            is_published=data.get('is_published', True),
            created_by=data.get('created_by')
        )
        
        db.session.add(tip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tip created successfully',
            'data': tip.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ✅ UPDATE TIP (Admin Dashboard Only)
@tips_bp.route('/<int:tip_id>', methods=['PUT'])
@require_admin
def update_tip(tip_id):
    try:
        tip = Tip.query.get_or_404(tip_id)
        data = request.get_json()
        
        tip.title = data.get('title', tip.title)
        tip.content = data.get('content', tip.content)
        tip.category = data.get('category', tip.category)
        tip.image_url = data.get('image_url', tip.image_url)
        tip.is_published = data.get('is_published', tip.is_published)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tip updated successfully',
            'data': tip.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ✅ DELETE TIP (Admin Dashboard Only)
@tips_bp.route('/<int:tip_id>', methods=['DELETE'])
@require_admin
def delete_tip(tip_id):
    try:
        tip = Tip.query.get_or_404(tip_id)
        db.session.delete(tip)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Tip deleted successfully'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500