from src.models.user import db
from datetime import datetime

class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text)
    tribunal = db.Column(db.String(100))
    publication_date = db.Column(db.DateTime)
    source_url = db.Column(db.String(500))
    process_number = db.Column(db.String(100))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamento
    user = db.relationship('User', backref=db.backref('publications', lazy=True))

    def __repr__(self):
        return f'<Publication {self.title[:50]}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'tribunal': self.tribunal,
            'publication_date': self.publication_date.isoformat() if self.publication_date else None,
            'source_url': self.source_url,
            'process_number': self.process_number,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

