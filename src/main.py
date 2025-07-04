import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.plan import plan_bp
from src.routes.subscription import subscription_bp
from src.routes.publication import publication_bp
from src.routes.search_config import search_config_bp
from src.routes.datajud import datajud_bp
from src.routes.search_target import search_target_bp
from src.routes.admin import admin_bp  # Novo blueprint administrativo
from src.services.comunicapje_service import run_daily_searches

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(plan_bp, url_prefix='/api')
app.register_blueprint(subscription_bp, url_prefix='/api')
app.register_blueprint(publication_bp, url_prefix='/api')
app.register_blueprint(search_config_bp, url_prefix='/api')
app.register_blueprint(datajud_bp, url_prefix="/api")
app.register_blueprint(search_target_bp, url_prefix="/api")
app.register_blueprint(admin_bp, url_prefix="/api")  # Registrar rotas administrativas

@app.route("/api/run-comunicapje-search", methods=["POST"])
def trigger_comunicapje_search():
    run_daily_searches()
    return jsonify({"message": "ComunicaPJE daily search triggered"}), 200

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Importar todos os modelos para garantir que sejam criados
from src.models.user import User
from src.models.plan import Plan
from src.models.subscription import Subscription
from src.models.publication import Publication
from src.models.search_config import SearchConfig
from src.models.search_target import SearchTarget
from src.models.admin import Admin

# Criar tabelas
with app.app_context():
    db.create_all()
    
    # Criar admin padrão se não existir
    admin = Admin.query.filter_by(username='admin').first()
    if not admin:
        admin = Admin(
            username='admin',
            email='admin@jurisalerta.com',
            full_name='Administrador JurisAlerta',
            is_super_admin=True
        )
        admin.set_password('admin123')  # Senha padrão - DEVE SER ALTERADA
        db.session.add(admin)
        db.session.commit()
        print("Admin padrão criado: admin / admin123")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

