from src.models.user import db
from datetime import datetime

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    max_searches = db.Column(db.Integer, default=100)  # Número máximo de pesquisas por mês
    max_tribunals = db.Column(db.Integer, default=5)   # Número máximo de tribunais monitorados
    max_targets = db.Column(db.Integer, default=10)    # Número máximo de alvos de busca
    features = db.Column(db.Text)                      # Recursos do plano
    is_active = db.Column(db.Boolean, default=True)    # Se o plano está ativo
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Plan {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'max_searches': self.max_searches,
            'max_tribunals': self.max_tribunals,
            'max_targets': self.max_targets,
            'features': self.features,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

