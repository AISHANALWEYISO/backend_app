from app import db

class Disease(db.Model):
    __tablename__ = 'diseases'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text)
    signs = db.Column(db.Text)
    prevention = db.Column(db.Text)
    treatment = db.Column(db.Text)
    image = db.Column(db.String(200))