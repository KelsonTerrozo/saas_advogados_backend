from flask import Blueprint, jsonify, request
from src.models.search_config import SearchConfig, db
from src.models.user import User

search_config_bp = Blueprint('search_config', __name__)

@search_config_bp.route('/search-configs', methods=['GET'])
def get_search_configs():
    """Retorna todas as configurações de pesquisa"""
    configs = SearchConfig.query.all()
    return jsonify([config.to_dict() for config in configs])

@search_config_bp.route('/search-configs', methods=['POST'])
def create_search_config():
    """Cria uma nova configuração de pesquisa"""
    data = request.json
    
    # Verificar se o usuário existe
    user = User.query.get_or_404(data['user_id'])
    
    # Converter listas para strings separadas por vírgula
    keywords = ','.join(data.get('keywords', [])) if isinstance(data.get('keywords'), list) else data.get('keywords', '')
    tribunals = ','.join(data.get('tribunals', [])) if isinstance(data.get('tribunals'), list) else data.get('tribunals', '')
    process_types = ','.join(data.get('process_types', [])) if isinstance(data.get('process_types'), list) else data.get('process_types', '')
    
    config = SearchConfig(
        user_id=data['user_id'],
        name=data['name'],
        keywords=keywords,
        tribunals=tribunals,
        process_types=process_types,
        is_active=data.get('is_active', True)
    )
    
    db.session.add(config)
    db.session.commit()
    return jsonify(config.to_dict()), 201

@search_config_bp.route('/search-configs/<int:config_id>', methods=['GET'])
def get_search_config(config_id):
    """Retorna uma configuração de pesquisa específica"""
    config = SearchConfig.query.get_or_404(config_id)
    return jsonify(config.to_dict())

@search_config_bp.route('/search-configs/user/<int:user_id>', methods=['GET'])
def get_user_search_configs(user_id):
    """Retorna todas as configurações de pesquisa de um usuário"""
    configs = SearchConfig.query.filter_by(user_id=user_id).all()
    return jsonify([config.to_dict() for config in configs])

@search_config_bp.route('/search-configs/user/<int:user_id>/active', methods=['GET'])
def get_user_active_search_configs(user_id):
    """Retorna as configurações de pesquisa ativas de um usuário"""
    configs = SearchConfig.query.filter_by(user_id=user_id, is_active=True).all()
    return jsonify([config.to_dict() for config in configs])

@search_config_bp.route('/search-configs/<int:config_id>', methods=['PUT'])
def update_search_config(config_id):
    """Atualiza uma configuração de pesquisa"""
    config = SearchConfig.query.get_or_404(config_id)
    data = request.json
    
    config.name = data.get('name', config.name)
    
    # Atualizar keywords
    if 'keywords' in data:
        keywords = ','.join(data['keywords']) if isinstance(data['keywords'], list) else data['keywords']
        config.keywords = keywords
    
    # Atualizar tribunals
    if 'tribunals' in data:
        tribunals = ','.join(data['tribunals']) if isinstance(data['tribunals'], list) else data['tribunals']
        config.tribunals = tribunals
    
    # Atualizar process_types
    if 'process_types' in data:
        process_types = ','.join(data['process_types']) if isinstance(data['process_types'], list) else data['process_types']
        config.process_types = process_types
    
    config.is_active = data.get('is_active', config.is_active)
    
    db.session.commit()
    return jsonify(config.to_dict())

@search_config_bp.route('/search-configs/<int:config_id>/toggle', methods=['PUT'])
def toggle_search_config(config_id):
    """Ativa/desativa uma configuração de pesquisa"""
    config = SearchConfig.query.get_or_404(config_id)
    config.is_active = not config.is_active
    db.session.commit()
    return jsonify(config.to_dict())

@search_config_bp.route('/search-configs/<int:config_id>', methods=['DELETE'])
def delete_search_config(config_id):
    """Remove uma configuração de pesquisa"""
    config = SearchConfig.query.get_or_404(config_id)
    db.session.delete(config)
    db.session.commit()
    return '', 204

