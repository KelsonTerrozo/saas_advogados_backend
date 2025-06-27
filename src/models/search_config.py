from src.models.user import db
from datetime import datetime

class SearchConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # Nome da configuração
    keywords = db.Column(db.Text)  # Palavras-chave separadas por vírgula
    tribunals = db.Column(db.Text)  # Tribunais separados por vírgula
    process_types = db.Column(db.Text)  # Tipos de processo
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento
    user = db.relationship('User', backref=db.backref('search_configs', lazy=True))

    def __repr__(self):
        return f'<SearchConfig {self.name}>'

    def get_keywords_list(self):
        return [k.strip() for k in self.keywords.split(',') if k.strip()] if self.keywords else []

    def get_tribunals_list(self):
        return [t.strip() for t in self.tribunals.split(',') if t.strip()] if self.tribunals else []

    def get_process_types_list(self):
        return [p.strip() for p in self.process_types.split(',') if p.strip()] if self.process_types else []

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'keywords': self.get_keywords_list(),
            'tribunals': self.get_tribunals_list(),
            'process_types': self.get_process_types_list(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

