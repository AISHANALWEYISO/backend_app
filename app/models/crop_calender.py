from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Crop(db.Model):
    __tablename__ = 'crops'

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    planting_time = db.Column(db.String(100), nullable=False)
    harvest_time  = db.Column(db.String(100), nullable=False)
    duration      = db.Column(db.String(100), nullable=False)
    season        = db.Column(db.String(100), nullable=False)   # e.g. "Rainy Season"
    tip           = db.Column(db.Text, nullable=True)
    color         = db.Column(db.String(10), nullable=False, default='#4CAF50')  # hex

    def to_dict(self):
        return {
            'id':            self.id,
            'name':          self.name,
            'planting_time': self.planting_time,
            'harvest_time':  self.harvest_time,
            'duration':      self.duration,
            'season':        self.season,
            'tip':           self.tip,
            'color':         self.color,
        }