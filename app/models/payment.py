# app/models/payment.py

from app import db
from datetime import datetime
from app.models.user import User

class PaymentOrder(db.Model):
    __tablename__ = 'payment_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ✅ String reference
    order_ref = db.Column(db.String(100), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default='UGX')
    credits_amount = db.Column(db.Integer, nullable=False)
    package = db.Column(db.String(50), nullable=False)
    
    # Payment details (user enters these)
    payment_method = db.Column(db.String(50))
    phone_number = db.Column(db.String(20))
    transaction_id = db.Column(db.String(100))
    
    # Status
    status = db.Column(db.String(20), default='pending')
    admin_note = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer, nullable=True)
    
    # ✅ Use lazy='select' to avoid loading issues
    user = db.relationship('User', backref=db.backref('payment_orders', lazy=True), lazy='select')
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_ref': self.order_ref,
            'user_id': self.user_id,
            'user_email': self.user.email if self.user else None,
            'user_name': self.user.name if self.user else None,
            'amount': self.amount,
            'currency': self.currency,
            'credits_amount': self.credits_amount,
            'package': self.package,
            'payment_method': self.payment_method,
            'phone_number': self.phone_number,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'admin_note': self.admin_note,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M') if self.created_at else None,
            'approved_at': self.approved_at.strftime('%Y-%m-%d %H:%M') if self.approved_at else None,
        }