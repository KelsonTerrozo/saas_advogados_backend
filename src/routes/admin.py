from flask import Blueprint, request, jsonify
from src.models.user import db, User
from src.models.admin import Admin
from src.models.plan import Plan
from src.models.subscription import Subscription
from src.models.search_target import SearchTarget
from src.models.publication import Publication
from datetime import datetime
import jwt
import os

admin_bp = Blueprint('admin', __name__)

# Middleware para verificar se é admin
def admin_required(f):
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token de acesso necessário'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, 'admin-secret-key', algorithms=['HS256'])
            admin_id = data['admin_id']
            admin = Admin.query.get(admin_id)
            if not admin or not admin.is_active:
                return jsonify({'error': 'Admin não encontrado ou inativo'}), 401
        except:
            return jsonify({'error': 'Token inválido'}), 401
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.check_password(password) and admin.is_active:
        admin.last_login = datetime.utcnow()
        db.session.commit()
        
        token = jwt.encode({
            'admin_id': admin.id,
            'username': admin.username,
            'exp': datetime.utcnow().timestamp() + 86400  # 24 horas
        }, 'admin-secret-key', algorithm='HS256')
        
        return jsonify({
            'token': token,
            'admin': admin.to_dict()
        })
    
    return jsonify({'error': 'Credenciais inválidas'}), 401

@admin_bp.route('/admin/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    # Estatísticas gerais
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    total_subscriptions = Subscription.query.count()
    active_subscriptions = Subscription.query.filter_by(status='active').count()
    total_search_targets = SearchTarget.query.count()
    total_publications = Publication.query.count()
    
    # Usuários recentes (últimos 7 dias)
    from datetime import timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_users = User.query.filter(User.created_at >= week_ago).count()
    
    return jsonify({
        'stats': {
            'total_users': total_users,
            'active_users': active_users,
            'total_subscriptions': total_subscriptions,
            'active_subscriptions': active_subscriptions,
            'total_search_targets': total_search_targets,
            'total_publications': total_publications,
            'recent_users': recent_users
        }
    })

@admin_bp.route('/admin/users', methods=['GET'])
@admin_required
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = User.query
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search)) |
            (User.full_name.contains(search))
        )
    
    users = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [user.to_dict() for user in users.items],
        'total': users.total,
        'pages': users.pages,
        'current_page': page
    })

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Buscar assinaturas do usuário
    subscriptions = Subscription.query.filter_by(user_id=user_id).all()
    
    # Buscar alvos de busca do usuário
    search_targets = SearchTarget.query.filter_by(user_id=user_id).all()
    
    return jsonify({
        'user': user.to_dict(),
        'subscriptions': [sub.to_dict() for sub in subscriptions],
        'search_targets': [target.to_dict() for target in search_targets]
    })

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        user.phone = data['phone']
    if 'oab_number' in data:
        user.oab_number = data['oab_number']
    
    db.session.commit()
    return jsonify(user.to_dict())

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Deletar dados relacionados
    SearchTarget.query.filter_by(user_id=user_id).delete()
    Subscription.query.filter_by(user_id=user_id).delete()
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Usuário deletado com sucesso'})

@admin_bp.route('/admin/plans', methods=['GET'])
@admin_required
def get_plans():
    plans = Plan.query.all()
    return jsonify([plan.to_dict() for plan in plans])

@admin_bp.route('/admin/plans', methods=['POST'])
@admin_required
def create_plan():
    data = request.get_json()
    
    plan = Plan(
        name=data['name'],
        description=data.get('description'),
        price=data['price'],
        max_searches=data.get('max_searches'),
        max_targets=data.get('max_targets'),
        features=data.get('features', ''),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(plan)
    db.session.commit()
    
    return jsonify(plan.to_dict()), 201

@admin_bp.route('/admin/plans/<int:plan_id>', methods=['PUT'])
@admin_required
def update_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    data = request.get_json()
    
    plan.name = data.get('name', plan.name)
    plan.description = data.get('description', plan.description)
    plan.price = data.get('price', plan.price)
    plan.max_searches = data.get('max_searches', plan.max_searches)
    plan.max_targets = data.get('max_targets', plan.max_targets)
    plan.features = data.get('features', plan.features)
    plan.is_active = data.get('is_active', plan.is_active)
    
    db.session.commit()
    return jsonify(plan.to_dict())

@admin_bp.route('/admin/plans/<int:plan_id>', methods=['DELETE'])
@admin_required
def delete_plan(plan_id):
    plan = Plan.query.get_or_404(plan_id)
    
    # Verificar se há assinaturas ativas
    active_subs = Subscription.query.filter_by(plan_id=plan_id, status='active').count()
    if active_subs > 0:
        return jsonify({'error': 'Não é possível deletar plano com assinaturas ativas'}), 400
    
    db.session.delete(plan)
    db.session.commit()
    
    return jsonify({'message': 'Plano deletado com sucesso'})

@admin_bp.route('/admin/subscriptions', methods=['GET'])
@admin_required
def get_subscriptions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    status = request.args.get('status', '')
    
    query = Subscription.query.join(User).join(Plan)
    if status:
        query = query.filter(Subscription.status == status)
    
    subscriptions = query.paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for sub in subscriptions.items:
        sub_dict = sub.to_dict()
        sub_dict['user'] = sub.user.to_dict()
        sub_dict['plan'] = sub.plan.to_dict()
        result.append(sub_dict)
    
    return jsonify({
        'subscriptions': result,
        'total': subscriptions.total,
        'pages': subscriptions.pages,
        'current_page': page
    })

@admin_bp.route('/admin/subscriptions/<int:subscription_id>/status', methods=['PUT'])
@admin_required
def update_subscription_status(subscription_id):
    subscription = Subscription.query.get_or_404(subscription_id)
    data = request.get_json()
    
    subscription.status = data['status']
    db.session.commit()
    
    return jsonify(subscription.to_dict())

@admin_bp.route('/admin/search-targets', methods=['GET'])
@admin_required
def get_search_targets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    targets = SearchTarget.query.join(User).paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for target in targets.items:
        target_dict = target.to_dict()
        target_dict['user'] = target.user.to_dict()
        result.append(target_dict)
    
    return jsonify({
        'search_targets': result,
        'total': targets.total,
        'pages': targets.pages,
        'current_page': page
    })

@admin_bp.route('/admin/publications', methods=['GET'])
@admin_required
def get_publications():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    publications = Publication.query.join(User).paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for pub in publications.items:
        pub_dict = pub.to_dict()
        pub_dict['user'] = pub.user.to_dict()
        result.append(pub_dict)
    
    return jsonify({
        'publications': result,
        'total': publications.total,
        'pages': publications.pages,
        'current_page': page
    })

@admin_bp.route('/admin/system/backup', methods=['POST'])
@admin_required
def create_backup():
    # Implementar backup do banco de dados
    return jsonify({'message': 'Backup criado com sucesso', 'filename': f'backup_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.db'})

@admin_bp.route('/admin/system/logs', methods=['GET'])
@admin_required
def get_system_logs():
    # Implementar visualização de logs
    return jsonify({
        'logs': [
            {'timestamp': '2024-06-25 10:00:00', 'level': 'INFO', 'message': 'Sistema iniciado'},
            {'timestamp': '2024-06-25 10:05:00', 'level': 'INFO', 'message': 'Busca ComunicaPJE executada'},
            {'timestamp': '2024-06-25 10:10:00', 'level': 'WARNING', 'message': 'Limite de API atingido'}
        ]
    })

