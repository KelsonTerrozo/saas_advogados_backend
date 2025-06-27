from flask import Blueprint, jsonify, request
from src.models.publication import Publication, db
from src.models.user import User
from datetime import datetime

publication_bp = Blueprint('publication', __name__)

@publication_bp.route('/publications', methods=['GET'])
def get_publications():
    """Retorna todas as publicações"""
    publications = Publication.query.all()
    return jsonify([publication.to_dict() for publication in publications])

@publication_bp.route('/publications', methods=['POST'])
def create_publication():
    """Cria uma nova publicação"""
    data = request.json
    
    # Verificar se o usuário existe
    user = User.query.get_or_404(data['user_id'])
    
    publication = Publication(
        user_id=data['user_id'],
        title=data['title'],
        content=data.get('content'),
        tribunal=data.get('tribunal'),
        publication_date=datetime.fromisoformat(data['publication_date']) if data.get('publication_date') else None,
        source_url=data.get('source_url'),
        process_number=data.get('process_number')
    )
    
    db.session.add(publication)
    db.session.commit()
    return jsonify(publication.to_dict()), 201

@publication_bp.route('/publications/<int:publication_id>', methods=['GET'])
def get_publication(publication_id):
    """Retorna uma publicação específica"""
    publication = Publication.query.get_or_404(publication_id)
    return jsonify(publication.to_dict())

@publication_bp.route('/publications/user/<int:user_id>', methods=['GET'])
def get_user_publications(user_id):
    """Retorna todas as publicações de um usuário"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    is_read = request.args.get('is_read', type=bool)
    
    query = Publication.query.filter_by(user_id=user_id)
    
    if is_read is not None:
        query = query.filter_by(is_read=is_read)
    
    publications = query.order_by(Publication.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'publications': [pub.to_dict() for pub in publications.items],
        'total': publications.total,
        'pages': publications.pages,
        'current_page': page,
        'per_page': per_page
    })

@publication_bp.route('/publications/<int:publication_id>/read', methods=['PUT'])
def mark_as_read(publication_id):
    """Marca uma publicação como lida"""
    publication = Publication.query.get_or_404(publication_id)
    publication.is_read = True
    db.session.commit()
    return jsonify(publication.to_dict())

@publication_bp.route('/publications/<int:publication_id>/unread', methods=['PUT'])
def mark_as_unread(publication_id):
    """Marca uma publicação como não lida"""
    publication = Publication.query.get_or_404(publication_id)
    publication.is_read = False
    db.session.commit()
    return jsonify(publication.to_dict())

@publication_bp.route('/publications/<int:publication_id>', methods=['DELETE'])
def delete_publication(publication_id):
    """Remove uma publicação"""
    publication = Publication.query.get_or_404(publication_id)
    db.session.delete(publication)
    db.session.commit()
    return '', 204

