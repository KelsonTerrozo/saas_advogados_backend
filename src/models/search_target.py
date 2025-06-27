from src.models.user import db
from datetime import datetime

class SearchTarget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("search_targets", lazy=True))
    oab_number = db.Column(db.String(20), nullable=False)
    oab_uf = db.Column(db.String(2), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<SearchTarget {self.oab_uf}{self.oab_number} for User {self.user.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'oab_number': self.oab_number,
            'oab_uf': self.oab_uf,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

