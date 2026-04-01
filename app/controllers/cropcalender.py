from app.models.crop_calender import db, Crop


class CropController:

    @staticmethod
    def get_all_crops():
      
        crops = Crop.query.order_by(Crop.name).all()
        return [c.to_dict() for c in crops]

    @staticmethod
    def get_crop_by_id(crop_id: int):
        
        crop = Crop.query.get(crop_id)
        return crop.to_dict() if crop else None

    @staticmethod
    def get_crops_by_season(season: str):
        """Return crops filtered by season name (case-insensitive)."""
        crops = Crop.query.filter(
            Crop.season.ilike(f'%{season}%')
        ).order_by(Crop.name).all()
        return [c.to_dict() for c in crops]

    @staticmethod
    def create_crop(data: dict):
        """Create and save a new crop. Returns the new crop dict or an error string."""
        required = ['name', 'planting_time', 'harvest_time', 'duration', 'season']
        for field in required:
            if not data.get(field):
                return None, f'Missing required field: {field}'

        crop = Crop(
            name          = data['name'].strip(),
            planting_time = data['planting_time'].strip(),
            harvest_time  = data['harvest_time'].strip(),
            duration      = data['duration'].strip(),
            season        = data['season'].strip(),
            tip           = data.get('tip', '').strip(),
            color         = data.get('color', '#4CAF50').strip(),
        )
        db.session.add(crop)
        db.session.commit()
        return crop.to_dict(), None

    @staticmethod
    def update_crop(crop_id: int, data: dict):
        """Update an existing crop. Returns updated dict or None if not found."""
        crop = Crop.query.get(crop_id)
        if not crop:
            return None, 'Crop not found'

        if 'name'          in data: crop.name          = data['name'].strip()
        if 'planting_time' in data: crop.planting_time = data['planting_time'].strip()
        if 'harvest_time'  in data: crop.harvest_time  = data['harvest_time'].strip()
        if 'duration'      in data: crop.duration      = data['duration'].strip()
        if 'season'        in data: crop.season        = data['season'].strip()
        if 'tip'           in data: crop.tip           = data['tip'].strip()
        if 'color'         in data: crop.color         = data['color'].strip()

        db.session.commit()
        return crop.to_dict(), None

    @staticmethod
    def delete_crop(crop_id: int):
        """Delete a crop by ID. Returns True if deleted, False if not found."""
        crop = Crop.query.get(crop_id)
        if not crop:
            return False
        db.session.delete(crop)
        db.session.commit()
        return True