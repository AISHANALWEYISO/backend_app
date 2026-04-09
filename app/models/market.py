from app.extensions import db
from datetime import datetime, timezone

class MarketItem(db.Model):
    __tablename__ = 'market_items'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)  # Seeds, Tools, Fertilizer, etc.
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default='kg')  # kg, piece, bag, etc.
    quantity_available = db.Column(db.Integer, default=0)
    seller_name = db.Column(db.String(100), nullable=False)
    seller_phone = db.Column(db.String(20))
    seller_location = db.Column(db.String(100))
    image = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'price': self.price,
            'unit': self.unit,
            'quantity_available': self.quantity_available,
            'seller_name': self.seller_name,
            'seller_phone': self.seller_phone,
            'seller_location': self.seller_location,
            'image': self.image,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }