from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.payment import PaymentOrder
import uuid
from datetime import datetime

payment_bp = Blueprint('payment', __name__)

# ── Package Prices ──
PACKAGES = {
    '1_scan': {'credits': 1, 'price_ugx': 12000},
    '5_scans': {'credits': 5, 'price_ugx': 50000},
    '10_scans': {'credits': 10, 'price_ugx': 90000},
    '20_scans': {'credits': 20, 'price_ugx': 160000},
}

# ── 1. User Initiates Payment (Creates Pending Order) ──
@payment_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    """
    User submits payment request with transaction ID
    POST /api/payment/initiate
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))
        
        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404
        
        data = request.get_json()
        package = data.get('package', '5_scans')
        
        if package not in PACKAGES:
            return jsonify({"success": False, "message": "Invalid package"}), 400
        
        package_info = PACKAGES[package]
        credits = package_info['credits']
        price = package_info['price_ugx']
        
        # Generate unique order reference
        order_ref = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create PENDING payment order (DO NOT add credits yet!)
        new_order = PaymentOrder(
            user_id=user.id,
            order_ref=order_ref,
            amount=price,
            currency='UGX',
            credits_amount=credits,
            package=package,
            payment_method=data.get('payment_method', 'MTN'),
            phone_number=data.get('phone_number', ''),
            transaction_id=data.get('transaction_id', ''),
            status='pending'
        )
        
        db.session.add(new_order)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Payment submitted for approval. Credits will be added after verification.",
            "order_ref": order_ref,
            "status": "pending",
            "credits_amount": credits,
            "amount": price
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ── 2. User Checks Their Payment Status ──
@payment_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """
    User checks their payment history
    GET /api/payment/my-orders
    """
    try:
        current_user_id = get_jwt_identity()
        orders = PaymentOrder.query.filter_by(user_id=int(current_user_id))\
            .order_by(PaymentOrder.created_at.desc()).all()
        
        return jsonify({
            "success": True,
            "orders": [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ── 3. Admin: Get All Pending Payments ──
@payment_bp.route('/admin/pending', methods=['GET'])
@jwt_required()
def get_pending_payments():
    """
    Admin views all pending payments
    GET /api/payment/admin/pending
    """
    try:
        # TODO: Add admin check here (verify user is admin)
        orders = PaymentOrder.query.filter_by(status='pending')\
            .order_by(PaymentOrder.created_at.desc()).all()
        
        return jsonify({
            "success": True,
            "orders": [order.to_dict() for order in orders]
        }), 200
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ── 4. Admin: Approve Payment (Adds Credits!) ──
@payment_bp.route('/admin/approve/<int:order_id>', methods=['POST'])
@jwt_required()
def approve_payment(order_id):
    """
    Admin approves payment and adds credits to user
    POST /api/payment/admin/approve/<order_id>
    """
    try:
        # TODO: Add admin check here
        current_user_id = get_jwt_identity()
        
        order = PaymentOrder.query.get(order_id)
        if not order:
            return jsonify({"success": False, "message": "Order not found"}), 404
        
        if order.status != 'pending':
            return jsonify({"success": False, "message": "Order already processed"}), 400
        
        # ✅ APPROVE: Add credits to user
        user = User.query.get(order.user_id)
        if user:
            user.soil_scan_credits += order.credits_amount
        
        # Update order status
        order.status = 'approved'
        order.approved_at = datetime.utcnow()
        order.approved_by = int(current_user_id)
        order.admin_note = request.get_json().get('note', 'Approved')
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Approved! {order.credits_amount} credits added to {user.email}",
            "credits_added": order.credits_amount
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ── 5. Admin: Reject Payment ──
@payment_bp.route('/admin/reject/<int:order_id>', methods=['POST'])
@jwt_required()
def reject_payment(order_id):
    """
    Admin rejects payment (invalid transaction ID, etc.)
    POST /api/payment/admin/reject/<order_id>
    """
    try:
        current_user_id = get_jwt_identity()
        
        order = PaymentOrder.query.get(order_id)
        if not order:
            return jsonify({"success": False, "message": "Order not found"}), 404
        
        order.status = 'rejected'
        order.admin_note = request.get_json().get('reason', 'Rejected')
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Payment rejected"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500