from src.models.user import db
from datetime import datetime, timedelta

class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=False)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='active')  # active, cancelled, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacionamentos
    user = db.relationship('User', backref=db.backref('subscriptions', lazy=True))
    plan = db.relationship('Plan', backref=db.backref('subscriptions', lazy=True))

    def __init__(self, user_id, plan_id, duration_months=1):
        self.user_id = user_id
        self.plan_id = plan_id
        self.start_date = datetime.utcnow()
        self.end_date = self.start_date + timedelta(days=30 * duration_months)

    def is_active(self):
        return self.status == 'active' and self.end_date > datetime.utcnow()

    def __repr__(self):
        return f'<Subscription User:{self.user_id} Plan:{self.plan_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan_id': self.plan_id,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'is_active': self.is_active(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

