# from flask import Blueprint, request, jsonify
# from flask_jwt_extended import jwt_required, get_jwt_identity
# from app import db
# from app.models.user import User
# from app.models.payment import PaymentOrder
# import uuid
# from datetime import datetime

# payment_bp = Blueprint('payment', __name__)

# # ── Package Prices ──
# PACKAGES = {
#     '1_scan': {'credits': 1, 'price_ugx': 12000},
#     '5_scans': {'credits': 5, 'price_ugx': 50000},
#     '10_scans': {'credits': 10, 'price_ugx': 90000},
#     '20_scans': {'credits': 20, 'price_ugx': 160000},
# }

# # ── 1. User Initiates Payment (Creates Pending Order) ──
# @payment_bp.route('/initiate', methods=['POST'])
# @jwt_required()
# def initiate_payment():
#     """
#     User submits payment request with transaction ID
#     POST /api/payment/initiate
#     """
#     try:
#         current_user_id = get_jwt_identity()
#         user = User.query.get(int(current_user_id))
        
#         if not user:
#             return jsonify({"success": False, "message": "User not found"}), 404
        
#         data = request.get_json()
#         package = data.get('package', '5_scans')
        
#         if package not in PACKAGES:
#             return jsonify({"success": False, "message": "Invalid package"}), 400
        
#         package_info = PACKAGES[package]
#         credits = package_info['credits']
#         price = package_info['price_ugx']
        
#         # Generate unique order reference
#         order_ref = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
#         # Create PENDING payment order (DO NOT add credits yet!)
#         new_order = PaymentOrder(
#             user_id=user.id,
#             order_ref=order_ref,
#             amount=price,
#             currency='UGX',
#             credits_amount=credits,
#             package=package,
#             payment_method=data.get('payment_method', 'MTN'),
#             phone_number=data.get('phone_number', ''),
#             transaction_id=data.get('transaction_id', ''),
#             status='pending'
#         )
        
#         db.session.add(new_order)
#         db.session.commit()
        
#         return jsonify({
#             "success": True,
#             "message": "Payment submitted for approval. Credits will be added after verification.",
#             "order_ref": order_ref,
#             "status": "pending",
#             "credits_amount": credits,
#             "amount": price
#         }), 201
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "message": str(e)}), 500


# # ── 2. User Checks Their Payment Status ──
# @payment_bp.route('/my-orders', methods=['GET'])
# @jwt_required()
# def get_my_orders():
#     """
#     User checks their payment history
#     GET /api/payment/my-orders
#     """
#     try:
#         current_user_id = get_jwt_identity()
#         orders = PaymentOrder.query.filter_by(user_id=int(current_user_id))\
#             .order_by(PaymentOrder.created_at.desc()).all()
        
#         return jsonify({
#             "success": True,
#             "orders": [order.to_dict() for order in orders]
#         }), 200
        
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500


# # ── 3. Admin: Get All Pending Payments ──
# @payment_bp.route('/admin/pending', methods=['GET'])
# @jwt_required()
# def get_pending_payments():
#     """
#     Admin views all pending payments
#     GET /api/payment/admin/pending
#     """
#     try:
#         # TODO: Add admin check here (verify user is admin)
#         orders = PaymentOrder.query.filter_by(status='pending')\
#             .order_by(PaymentOrder.created_at.desc()).all()
        
#         return jsonify({
#             "success": True,
#             "orders": [order.to_dict() for order in orders]
#         }), 200
        
#     except Exception as e:
#         return jsonify({"success": False, "message": str(e)}), 500


# # ── 4. Admin: Approve Payment (Adds Credits!) ──
# @payment_bp.route('/admin/approve/<int:order_id>', methods=['POST'])
# @jwt_required()
# def approve_payment(order_id):
#     """
#     Admin approves payment and adds credits to user
#     POST /api/payment/admin/approve/<order_id>
#     """
#     try:
#         # TODO: Add admin check here
#         current_user_id = get_jwt_identity()
        
#         order = PaymentOrder.query.get(order_id)
#         if not order:
#             return jsonify({"success": False, "message": "Order not found"}), 404
        
#         if order.status != 'pending':
#             return jsonify({"success": False, "message": "Order already processed"}), 400
        
#         # ✅ APPROVE: Add credits to user
#         user = User.query.get(order.user_id)
#         if user:
#             user.soil_scan_credits += order.credits_amount
        
#         # Update order status
#         order.status = 'approved'
#         order.approved_at = datetime.utcnow()
#         order.approved_by = int(current_user_id)
#         order.admin_note = request.get_json().get('note', 'Approved')
        
#         db.session.commit()
        
#         return jsonify({
#             "success": True,
#             "message": f"Approved! {order.credits_amount} credits added to {user.email}",
#             "credits_added": order.credits_amount
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "message": str(e)}), 500


# # ── 5. Admin: Reject Payment ──
# @payment_bp.route('/admin/reject/<int:order_id>', methods=['POST'])
# @jwt_required()
# def reject_payment(order_id):
#     """
#     Admin rejects payment (invalid transaction ID, etc.)
#     POST /api/payment/admin/reject/<order_id>
#     """
#     try:
#         current_user_id = get_jwt_identity()
        
#         order = PaymentOrder.query.get(order_id)
#         if not order:
#             return jsonify({"success": False, "message": "Order not found"}), 404
        
#         order.status = 'rejected'
#         order.admin_note = request.get_json().get('reason', 'Rejected')
        
#         db.session.commit()
        
#         return jsonify({
#             "success": True,
#             "message": "Payment rejected"
#         }), 200
        
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"success": False, "message": str(e)}), 500


from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.payment import PaymentOrder
from services.email_service import (
    email_order_created,
    email_admin_new_payment,
    email_payment_approved,
    email_payment_rejected,
)
import uuid
from datetime import datetime
import os

payment_bp = Blueprint('payment', __name__)

MTN_NUMBER    = os.getenv('MTN_NUMBER',    '0766753527')
AIRTEL_NUMBER = os.getenv('AIRTEL_NUMBER', '0750163604')

# ── Package Prices ────────────────────────────────────────────────────────────
PACKAGES = {
    '1_scan':   {'credits': 1,  'price_ugx': 12000},
    '5_scans':  {'credits': 5,  'price_ugx': 50000},
    '10_scans': {'credits': 10, 'price_ugx': 90000},
    '20_scans': {'credits': 20, 'price_ugx': 160000},
}


# ── 1. Get Payment Info (numbers + packages) ──────────────────────────────────
@payment_bp.route('/info', methods=['GET'])
def payment_info():
    """
    Returns your mobile money numbers and available packages.
    Flutter app calls this to show the payment screen.
    GET /api/payment/info
    """
    return jsonify({
        "success": True,
        "mtn_number":    MTN_NUMBER,
        "airtel_number": AIRTEL_NUMBER,
        "packages": [
            {
                "key":     key,
                "credits": info["credits"],
                "amount":  info["price_ugx"],
                "label":   f"{info['credits']} Scan(s) – UGX {info['price_ugx']:,}"
            }
            for key, info in PACKAGES.items()
        ],
        "instructions": [
            "1. Choose a package below",
            "2. Send mobile money to our number shown",
            "3. Use your Order Reference as the reason",
            "4. Check your email for payment instructions",
            "5. Enter the Transaction ID from your SMS",
            "6. Credits added after verification!"
        ]
    }), 200


# ── 2. Initiate Payment (Creates Order + Emails Farmer) ──────────────────────
@payment_bp.route('/initiate', methods=['POST'])
@jwt_required()
def initiate_payment():
    """
    Farmer selects a package → order is created → email sent with instructions.
    POST /api/payment/initiate
    Body: { "package": "5_scans", "payment_method": "MTN", "phone_number": "07XX" }
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(int(current_user_id))

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        data           = request.get_json()
        package_key    = data.get('package', '5_scans')
        payment_method = data.get('payment_method', 'MTN').upper()
        phone_number   = data.get('phone_number', '')

        if package_key not in PACKAGES:
            return jsonify({"success": False, "message": "Invalid package"}), 400

        if payment_method not in ['MTN', 'AIRTEL']:
            return jsonify({"success": False, "message": "Payment method must be MTN or AIRTEL"}), 400

        package_info = PACKAGES[package_key]
        credits      = package_info['credits']
        price        = package_info['price_ugx']
        send_to      = MTN_NUMBER if payment_method == 'MTN' else AIRTEL_NUMBER

        # Generate unique order reference
        order_ref = f"YUCCA-{uuid.uuid4().hex[:8].upper()}"

        # Create PENDING order (no credits yet!)
        new_order = PaymentOrder(
            user_id        = user.id,
            order_ref      = order_ref,
            amount         = price,
            currency       = 'UGX',
            credits_amount = credits,
            package        = package_key,
            payment_method = payment_method,
            phone_number   = phone_number,
            status         = 'pending'
        )
        db.session.add(new_order)
        db.session.commit()

        # ✉️ Email farmer with payment instructions
        email_order_created(
            farmer_name    = user.name,
            farmer_email   = user.email,
            order_ref      = order_ref,
            amount         = price,
            credits        = credits,
            package        = package_key,
            payment_method = payment_method,
        )

        return jsonify({
            "success":        True,
            "message":        f"Order created! Check your email ({user.email}) for payment instructions.",
            "order_ref":      order_ref,
            "amount":         price,
            "credits_amount": credits,
            "send_to":        send_to,
            "payment_method": payment_method,
            "status":         "pending"
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ── 3. Submit Transaction ID (Farmer enters ID from SMS) ─────────────────────
@payment_bp.route('/submit-transaction', methods=['POST'])
@jwt_required()
def submit_transaction():
    """
    Farmer receives MTN/Airtel SMS → copies Transaction ID → submits here.
    POST /api/payment/submit-transaction
    Body: { "order_ref": "YUCCA-XXXXX", "transaction_id": "TXN123456" }
    """
    try:
        current_user_id = get_jwt_identity()
        user            = User.query.get(int(current_user_id))
        data            = request.get_json()

        order_ref      = data.get('order_ref')
        transaction_id = data.get('transaction_id', '').strip()

        if not order_ref or not transaction_id:
            return jsonify({
                "success": False,
                "message": "Order reference and transaction ID are required"
            }), 400

        order = PaymentOrder.query.filter_by(
            order_ref = order_ref,
            user_id   = int(current_user_id)
        ).first()

        if not order:
            return jsonify({"success": False, "message": "Order not found"}), 404

        if order.status == 'approved':
            return jsonify({"success": False, "message": "This order is already approved"}), 400

        if order.status == 'rejected':
            return jsonify({"success": False, "message": "This order was rejected. Please create a new order"}), 400

        # Save transaction ID
        order.transaction_id = transaction_id
        order.status         = 'pending_verification'
        db.session.commit()

        # ✉️ Email admin (Aisha) to verify and approve
        email_admin_new_payment(
            farmer_name    = user.name,
            farmer_email   = user.email,
            farmer_phone   = order.phone_number,
            order_ref      = order_ref,
            amount         = order.amount,
            credits        = order.credits_amount,
            package        = order.package,
            payment_method = order.payment_method,
            transaction_id = transaction_id,
            order_id       = order.id,
        )

        return jsonify({
            "success":   True,
            "message":   "Transaction ID submitted! We are verifying your payment. You will receive a confirmation email shortly.",
            "order_ref": order_ref,
            "status":    "pending_verification"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ── 4. Check Order Status ─────────────────────────────────────────────────────
@payment_bp.route('/my-orders', methods=['GET'])
@jwt_required()
def get_my_orders():
    """
    Farmer checks their payment history.
    GET /api/payment/my-orders
    """
    try:
        current_user_id = get_jwt_identity()
        orders = PaymentOrder.query.filter_by(user_id=int(current_user_id))\
            .order_by(PaymentOrder.created_at.desc()).all()

        return jsonify({
            "success": True,
            "orders":  [order.to_dict() for order in orders]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ── 5. Admin: Get All Pending Payments ───────────────────────────────────────
@payment_bp.route('/admin/pending', methods=['GET'])
@jwt_required()
def get_pending_payments():
    """
    Admin views all pending payments.
    GET /api/payment/admin/pending
    """
    try:
        current_user_id = get_jwt_identity()
        admin           = User.query.get(int(current_user_id))

        if not admin or admin.usertype != 'admin':
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        orders = PaymentOrder.query\
            .filter(PaymentOrder.status.in_(['pending', 'pending_verification']))\
            .order_by(PaymentOrder.created_at.desc()).all()

        return jsonify({
            "success": True,
            "count":   len(orders),
            "orders":  [order.to_dict() for order in orders]
        }), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


# ── 6. Admin: Approve Payment ────────────────────────────────────────────────
@payment_bp.route('/admin/approve/<int:order_id>', methods=['POST'])
@jwt_required()
def approve_payment(order_id):
    """
    Admin approves payment → credits added → email sent to farmer.
    POST /api/payment/admin/approve/<order_id>
    Body: { "note": "Confirmed on MTN" }   (optional)
    """
    try:
        current_user_id = get_jwt_identity()
        admin           = User.query.get(int(current_user_id))

        if not admin or admin.usertype != 'admin':
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        order = PaymentOrder.query.get(order_id)
        if not order:
            return jsonify({"success": False, "message": "Order not found"}), 404

        if order.status == 'approved':
            return jsonify({"success": False, "message": "Order already approved"}), 400

        # ✅ Add credits to farmer
        farmer = User.query.get(order.user_id)
        if farmer:
            farmer.soil_scan_credits += order.credits_amount

        # Update order
        order.status      = 'approved'
        order.approved_at = datetime.utcnow()
        order.approved_by = int(current_user_id)
        order.admin_note  = request.get_json().get('note', 'Payment verified and approved')

        db.session.commit()

        # ✉️ Email farmer confirmation
        email_payment_approved(
            farmer_name   = farmer.name,
            farmer_email  = farmer.email,
            order_ref     = order.order_ref,
            credits       = order.credits_amount,
            total_credits = farmer.soil_scan_credits,
        )

        return jsonify({
            "success":       True,
            "message":       f"✅ Approved! {order.credits_amount} credits added to {farmer.name}. Email sent to {farmer.email}.",
            "credits_added": order.credits_amount,
            "total_credits": farmer.soil_scan_credits,
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500


# ── 7. Admin: Reject Payment ─────────────────────────────────────────────────
@payment_bp.route('/admin/reject/<int:order_id>', methods=['POST'])
@jwt_required()
def reject_payment(order_id):
    """
    Admin rejects payment → email sent to farmer explaining why.
    POST /api/payment/admin/reject/<order_id>
    Body: { "reason": "Transaction ID not found" }
    """
    try:
        current_user_id = get_jwt_identity()
        admin           = User.query.get(int(current_user_id))

        if not admin or admin.usertype != 'admin':
            return jsonify({"success": False, "message": "Unauthorized"}), 403

        order = PaymentOrder.query.get(order_id)
        if not order:
            return jsonify({"success": False, "message": "Order not found"}), 404

        reason           = request.get_json().get('reason', 'Payment could not be verified')
        order.status     = 'rejected'
        order.admin_note = reason
        db.session.commit()

        farmer = User.query.get(order.user_id)

        # ✉️ Email farmer rejection reason
        email_payment_rejected(
            farmer_name  = farmer.name,
            farmer_email = farmer.email,
            order_ref    = order.order_ref,
            reason       = reason,
        )

        return jsonify({
            "success": True,
            "message": f"❌ Payment rejected. Farmer ({farmer.email}) has been notified by email."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500