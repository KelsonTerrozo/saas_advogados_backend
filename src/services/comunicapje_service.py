import requests
import json
from datetime import date
from src.models.user import User
from src.models.search_target import SearchTarget
from src.models.user import db # Importar db do user.py para inicializar

API_BASE_URL = "https://comunicaapi.pje.jus.br"

def obter_certidao(hash_certidao):
    # Stub para a função obter_certidao
    # Em um ambiente real, esta função faria uma requisição para obter o PDF da certidão
    print(f"DEBUG: Solicitada certidão para hash: {hash_certidao}")
    return None # Retorna None por enquanto

def enviar_email_notificacao(assunto, corpo_html, destinatario, anexos=None):
    # Stub para a função enviar_email_notificacao
    # Em um ambiente real, esta função usaria um serviço de envio de e-mails (e.g., SendGrid, Mailgun)
    print(f"DEBUG: Enviando e-mail para {destinatario} com assunto: {assunto}")
    print("DEBUG: Conteúdo HTML (parcial):", corpo_html[:200])
    if anexos:
        print(f"DEBUG: Anexos: {len(anexos)}")
    return True

def formatar_email_html(target_str, items):
    """Cria o corpo do email em HTML."""
    
    processos_unicos = sorted(list(set(item.get('numeroprocessocommascara', 'N/A') for item in items)))

    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 700px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }}
            .header {{ background-color: #003366; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .publication {{ background-color: #ffffff; padding: 20px; margin-top: 20px; border: 1px solid #eee; border-radius: 8px; }}
            h1, h2, h3 {{ color: #003366; }}
            h2 {{ font-size: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
            .summary {{ background-color: #e7f0f7; padding: 15px; border-left: 4px solid #0056b3; margin-bottom: 20px; border-radius: 4px; }}
            .cta-button {{ display: inline-block; background-color: #28a745; color: white; padding: 10px 15px; text-decoration: none; border-radius: 5px; font-weight: bold; margin-top: 15px; }}
            .footer {{ text-align: center; font-size: 12px; color: #888; margin-top: 30px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>JurisAlerta</h1>
                <p style="color: #ccc; font-size: 16px;">Notificação de Novas Publicações</p>
            </div>
            
            <div class="summary">
                <p>Olá! Encontramos <strong>{len(items)} nova(s) publicação(ões)</strong> para o seu alvo de busca: <strong>{target_str}</strong>.</p>
                <p><strong>Processos envolvidos:</strong> {', '.join(processos_unicos)}</p>
            </div>

    """
    for item in items:
        partes_polo_a = [p['nome'] for p in item.get('destinatarios', []) if p['polo'] == 'A']
        partes_polo_p = [p['nome'] for p in item.get('destinatarios', []) if p['polo'] == 'P']
        texto_formatado = item.get('texto', '').replace('\n', '<br>')

        html += f"""
        <div class="publication">
            <h2>Processo: {item.get('numeroprocessocommascara', 'N/A')}</h2>
            <p>
                <strong>Data de Disponibilização:</strong> {item.get('datadisponibilizacao', 'N/A')}<br>
                <strong>Tipo de Comunicação:</strong> {item.get('tipoComunicacao', 'N/A')}<br>
                <strong>Órgão Julgador:</strong> {item.get('nomeOrgao', 'N/A')}
            </p>

            <h3>Partes Envolvidas</h3>
            <p><strong>Polo Ativo:</strong> {', '.join(partes_polo_a) or 'N/A'}</p>
            <p><strong>Polo Passivo:</strong> {', '.join(partes_polo_p) or 'N/A'}</p>

            <h3>Texto da Publicação</h3>
            <p>{texto_formatado}</p>

            <a href="{item.get('link', '#')}" class="cta-button" target="_blank">Acessar Publicação no PJe</a>
        </div>
        """
    
    html += """
            <p class="footer">
                As certidões em PDF e os detalhes técnicos (JSON) de cada publicação estão em anexo.<br>
                Este é um email automático enviado pelo sistema JurisAlerta.
            </p>
        </div>
    </body>
    </html>
    """
    return html

def run_daily_searches():
    print("--- Iniciando o robô de busca e notificação ---")
    
    active_targets = SearchTarget.query.filter_by(is_active=True).filter(SearchTarget.oab_number != "").all()
    data_hoje = date.today().strftime("%Y-%m-%d")

    for target in active_targets:
        target_str = f'{target.oab_uf.upper()}{target.oab_number}'
        print(f'\n--- Processando alvo: {target_str} (Usuário: {target.user.username}) ---')
        
        params = {
            "numeroOab": target.oab_number,
            "ufOab": target.oab_uf,
            "dataDisponibilizacaoInicio": data_hoje,
            "dataDisponibilizacaoFim": data_hoje,
        }

        try:
            response = requests.get(f"{API_BASE_URL}/api/v1/comunicacao", params=params, timeout=30)
            response.raise_for_status()
            resultados = response.json()
            total_encontrado = resultados.get("count", 0)

            if total_encontrado > 0:
                print(f'>>> SUCESSO! {total_encontrado} publicação(ões) encontrada(s).')
                
                items = resultados.get("items", [])
                anexos = []
                
                for item in items:
                    hash_certidao = item.get("hash")
                    if hash_certidao:
                        # Anexa a certidão em PDF
                        conteudo_pdf = obter_certidao(hash_certidao)
                        if conteudo_pdf:
                            anexos.append({
                                'nome': f'certidao_{hash_certidao}.pdf',
                                'conteudo': conteudo_pdf
                            })
                        
                        # Anexa os detalhes em JSON
                        detalhes_json = json.dumps(item, indent=2, ensure_ascii=False)
                        anexos.append({
                            'nome': f'detalhes_{hash_certidao}.json',
                            'conteudo': detalhes_json.encode('utf-8') # Converte string para bytes
                        })
                
                assunto = f"JurisAlerta: {total_encontrado} Novas Publicações para {target_str}"
                corpo_html = formatar_email_html(target_str, items)
                destinatario = target.user.email
                
                enviar_email_notificacao(assunto, corpo_html, destinatario, anexos)

            else:
                print(f'Nenhuma publicação nova para {target_str}.')

        except requests.exceptions.RequestException as e:
            print(f'Erro ao buscar para a OAB {target_str}: {e}')

    print('\n--- Robô finalizado com sucesso! ---')