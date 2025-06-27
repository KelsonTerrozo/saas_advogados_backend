from flask import Blueprint, jsonify, request
from src.models.subscription import Subscription, db
from src.models.user import User
from src.models.plan import Plan

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/subscriptions', methods=['GET'])
def get_subscriptions():
    """Retorna todas as assinaturas"""
    subscriptions = Subscription.query.all()
    return jsonify([subscription.to_dict() for subscription in subscriptions])

@subscription_bp.route('/subscriptions', methods=['POST'])
def create_subscription():
    """Cria uma nova assinatura"""
    data = request.json
    
    # Verificar se o usuário e plano existem
    user = User.query.get_or_404(data['user_id'])
    plan = Plan.query.get_or_404(data['plan_id'])
    
    subscription = Subscription(
        user_id=data['user_id'],
        plan_id=data['plan_id'],
        duration_months=data.get('duration_months', 1)
    )
    
    db.session.add(subscription)
    db.session.commit()
    return jsonify(subscription.to_dict()), 201

@subscription_bp.route('/subscriptions/<int:subscription_id>', methods=['GET'])
def get_subscription(subscription_id):
    """Retorna uma assinatura específica"""
    subscription = Subscription.query.get_or_404(subscription_id)
    return jsonify(subscription.to_dict())

@subscription_bp.route('/subscriptions/user/<int:user_id>', methods=['GET'])
def get_user_subscriptions(user_id):
    """Retorna todas as assinaturas de um usuário"""
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    return jsonify([subscription.to_dict() for subscription in subscriptions])

@subscription_bp.route('/subscriptions/user/<int:user_id>/active', methods=['GET'])
def get_user_active_subscription(user_id):
    """Retorna a assinatura ativa de um usuário"""
    subscription = Subscription.query.filter_by(
        user_id=user_id, 
        status='active'
    ).first()
    
    if subscription and subscription.is_active():
        return jsonify(subscription.to_dict())
    else:
        return jsonify({'message': 'Nenhuma assinatura ativa encontrada'}), 404

@subscription_bp.route('/subscriptions/<int:subscription_id>/cancel', methods=['PUT'])
def cancel_subscription(subscription_id):
    """Cancela uma assinatura"""
    subscription = Subscription.query.get_or_404(subscription_id)
    subscription.status = 'cancelled'
    db.session.commit()
    return jsonify(subscription.to_dict())

@subscription_bp.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
def delete_subscription(subscription_id):
    """Remove uma assinatura"""
    subscription = Subscription.query.get_or_404(subscription_id)
    db.session.delete(subscription)
    db.session.commit()
    return '', 204

