from flask import Blueprint, jsonify, request
from src.services.datajud_service import DataJudService

datajud_bp = Blueprint('datajud', __name__)
datajud_service = DataJudService()

@datajud_bp.route('/datajud/processes/search', methods=['GET'])
def search_processes():
    """Busca processos na API do DataJud"""
    
    # Obter parâmetros da query string
    numero_processo = request.args.get('numero_processo')
    tribunal = request.args.get('tribunal')
    classe = request.args.get('classe')
    assunto = request.args.get('assunto')
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    page = request.args.get('page', 1, type=int)
    size = request.args.get('size', 20, type=int)
    
    result = datajud_service.search_processes(
        numero_processo=numero_processo,
        tribunal=tribunal,
        classe=classe,
        assunto=assunto,
        data_inicio=data_inicio,
        data_fim=data_fim,
        page=page,
        size=size
    )
    
    if result.get('error'):
        return jsonify(result), 500
    
    return jsonify(result)

@datajud_bp.route('/datajud/processes/<processo_id>', methods=['GET'])
def get_process_details(processo_id):
    """Obtém detalhes de um processo específico"""
    
    result = datajud_service.get_process_details(processo_id)
    
    if result.get('error'):
        return jsonify(result), 500
    
    return jsonify(result)

@datajud_bp.route('/datajud/processes/<processo_id>/movements', methods=['GET'])
def get_process_movements(processo_id):
    """Obtém movimentações de um processo"""
    
    result = datajud_service.get_process_movements(processo_id)
    
    if result.get('error'):
        return jsonify(result), 500
    
    return jsonify(result)

@datajud_bp.route('/datajud/tribunals', methods=['GET'])
def get_tribunals():
    """Obtém lista de tribunais disponíveis"""
    
    result = datajud_service.get_tribunals()
    
    if result.get('error'):
        return jsonify(result), 500
    
    return jsonify(result)

@datajud_bp.route('/datajud/classes', methods=['GET'])
def get_process_classes():
    """Obtém lista de classes processuais"""
    
    result = datajud_service.get_process_classes()
    
    if result.get('error'):
        return jsonify(result), 500
    
    return jsonify(result)

@datajud_bp.route('/datajud/subjects', methods=['GET'])
def get_process_subjects():
    """Obtém lista de assuntos processuais"""
    
    result = datajud_service.get_process_subjects()
    
    if result.get('error'):
        return jsonify(result), 500
    
    return jsonify(result)

