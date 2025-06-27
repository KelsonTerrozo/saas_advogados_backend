from flask import Blueprint, jsonify, request
from src.models.plan import Plan, db

plan_bp = Blueprint('plan', __name__)

@plan_bp.route('/plans', methods=['GET'])
def get_plans():
    """Retorna todos os planos disponíveis"""
    plans = Plan.query.all()
    return jsonify([plan.to_dict() for plan in plans])

@plan_bp.route('/plans', methods=['POST'])
def create_plan():
    """Cria um novo plano"""
    data = request.json
    plan = Plan(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        max_searches=data.get('max_searches', 100),
        max_tribunals=data.get('max_tribunals', 5)
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify(plan.to_dict()), 201

@plan_bp.route('/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Retorna um plano específico"""
    plan = Plan.query.get_or_404(plan_id)
    return jsonify(plan.to_dict())

@plan_bp.route('/plans/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    """Atualiza um plano"""
    plan = Plan.query.get_or_404(plan_id)
    data = request.json
    
    plan.name = data.get('name', plan.name)
    plan.description = data.get('description', plan.description)
    plan.price = data.get('price', plan.price)
    plan.max_searches = data.get('max_searches', plan.max_searches)
    plan.max_tribunals = data.get('max_tribunals', plan.max_tribunals)
    
    db.session.commit()
    return jsonify(plan.to_dict())

@plan_bp.route('/plans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """Remove um plano"""
    plan = Plan.query.get_or_404(plan_id)
    db.session.delete(plan)
    db.session.commit()
    return '', 204

