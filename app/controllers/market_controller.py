import os
import uuid
from flask import Blueprint, request, jsonify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.market import MarketItem

market_bp = Blueprint('market', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
UPLOAD_FOLDER = 'static/uploads/market'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@market_bp.route('/', methods=['GET'])
def get_all_items():
    try:
        category = request.args.get('category')
        search = request.args.get('search')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        
        stmt = select(MarketItem)
        
        if category and category != 'All':
            stmt = stmt.where(MarketItem.category == category)
        if search:
            query = f'%{search}%'
            stmt = stmt.where(
                MarketItem.name.ilike(query) | 
                MarketItem.description.ilike(query)
            )
        if min_price is not None:
            stmt = stmt.where(MarketItem.price >= min_price)
        if max_price is not None:
            stmt = stmt.where(MarketItem.price <= max_price)
            
        stmt = stmt.order_by(MarketItem.created_at.desc())
        items = db.session.scalars(stmt).all()
        
        return jsonify({'success': True, 'data': [item.to_dict() for item in items]}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch items', 'error': str(e)}), 500

@market_bp.route('/<int:item_id>', methods=['GET'])
def get_item(item_id):
    try:
        item = db.session.get(MarketItem, item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404
        return jsonify({'success': True, 'data': item.to_dict()}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to fetch item', 'error': str(e)}), 500

@market_bp.route('/', methods=['POST'])
@jwt_required()
def create_item():
    try:
        if request.files:
            name = request.form.get('name', '').strip()
            category = request.form.get('category', '').strip()
            price = request.form.get('price', type=float)
            
            if not name or not category or price is None:
                return jsonify({'success': False, 'message': 'Name, category, and price are required'}), 400

            image_url = None
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                image_url = f"/static/uploads/market/{filename}"

            item = MarketItem(
                name=name,
                description=request.form.get('description', '').strip(),
                category=category,
                price=price,
                unit=request.form.get('unit', 'kg'),
                quantity_available=request.form.get('quantity_available', type=int, default=0),
                seller_name=request.form.get('seller_name', '').strip(),
                seller_phone=request.form.get('seller_phone', '').strip(),
                seller_location=request.form.get('seller_location', '').strip(),
                image=image_url
            )
        else:
            data = request.get_json()
            if not data:  # ✅ Fixed: was 'if not'
                return jsonify({'success': False, 'message': 'Request body must be JSON'}), 400
                
            name = data.get('name', '').strip()
            category = data.get('category', '').strip()
            price = data.get('price')
            
            if not name or not category or price is None:
                return jsonify({'success': False, 'message': 'Name, category, and price are required'}), 400

            item = MarketItem(
                name=name,
                description=data.get('description', '').strip(),
                category=category,
                price=price,
                unit=data.get('unit', 'kg'),
                quantity_available=data.get('quantity_available', 0),
                seller_name=data.get('seller_name', '').strip(),
                seller_phone=data.get('seller_phone', '').strip(),
                seller_location=data.get('seller_location', '').strip(),
                image=data.get('image_url')
            )
            
        db.session.add(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item listed', 'data': item.to_dict()}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

@market_bp.route('/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_item(item_id):
    try:
        item = db.session.get(MarketItem, item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404

        if request.files:
            file = request.files.get('image')
            if file and file.filename and allowed_file(file.filename):
                if item.image:
                    old_name = item.image.split('/')[-1]
                    old_path = os.path.join(UPLOAD_FOLDER, old_name)
                    if os.path.exists(old_path): os.remove(old_path)
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4().hex}.{ext}"
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(os.path.join(UPLOAD_FOLDER, filename))
                item.image = f"/static/uploads/market/{filename}"
                
            if 'name' in request.form: item.name = request.form['name'].strip()
            if 'description' in request.form: item.description = request.form['description'].strip()
            if 'category' in request.form: item.category = request.form['category'].strip()
            if 'price' in request.form: item.price = request.form.get('price', type=float)
            if 'unit' in request.form: item.unit = request.form['unit']
            if 'quantity_available' in request.form: item.quantity_available = request.form.get('quantity_available', type=int)
            if 'seller_name' in request.form: item.seller_name = request.form['seller_name'].strip()
            if 'seller_phone' in request.form: item.seller_phone = request.form['seller_phone'].strip()
            if 'seller_location' in request.form: item.seller_location = request.form['seller_location'].strip()
        else:
            data = request.get_json()
            if not data:  # ✅ Fixed: was 'if not'
                return jsonify({'success': False, 'message': 'No update data provided'}), 400
                
            if 'name' in data: item.name = data['name'].strip()  # ✅ Fixed: was 'if 'name' in'
            if 'description' in data: item.description = data['description'].strip()
            if 'category' in data: item.category = data['category'].strip()
            if 'price' in data: item.price = data['price']
            if 'unit' in data: item.unit = data['unit']
            if 'quantity_available' in data: item.quantity_available = data['quantity_available']
            if 'seller_name' in data: item.seller_name = data['seller_name'].strip()
            if 'seller_phone' in data: item.seller_phone = data['seller_phone'].strip()
            if 'seller_location' in data: item.seller_location = data['seller_location'].strip()
            if 'image_url' in data: item.image = data['image_url']

        db.session.commit()
        return jsonify({'success': True, 'message': 'Item updated', 'data': item.to_dict()}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500

@market_bp.route('/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_item(item_id):
    try:
        item = db.session.get(MarketItem, item_id)
        if not item:
            return jsonify({'success': False, 'message': 'Item not found'}), 404

        if item.image:
            img_name = item.image.split('/')[-1]
            img_path = os.path.join(UPLOAD_FOLDER, img_name)
            if os.path.exists(img_path): os.remove(img_path)

        db.session.delete(item)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Item removed'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error', 'error': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Unexpected error', 'error': str(e)}), 500