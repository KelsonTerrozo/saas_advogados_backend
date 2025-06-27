import requests
from datetime import datetime
from typing import List, Dict, Optional

class DataJudService:
    """Serviço para integração com a API Pública do DataJud"""
    
    def __init__(self):
        self.base_url = "https://api-publica.datajud.cnj.jus.br"
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'SaaS-Advogados/1.0'
        }
    
    def search_processes(self, 
                        numero_processo: Optional[str] = None,
                        tribunal: Optional[str] = None,
                        classe: Optional[str] = None,
                        assunto: Optional[str] = None,
                        data_inicio: Optional[str] = None,
                        data_fim: Optional[str] = None,
                        page: int = 1,
                        size: int = 20) -> Dict:
        """
        Busca processos na API do DataJud
        
        Args:
            numero_processo: Número do processo
            tribunal: Código do tribunal
            classe: Classe processual
            assunto: Assunto do processo
            data_inicio: Data de início (formato YYYY-MM-DD)
            data_fim: Data de fim (formato YYYY-MM-DD)
            page: Página da consulta
            size: Tamanho da página
            
        Returns:
            Dict com os resultados da busca
        """
        
        params = {
            'page': page,
            'size': size
        }
        
        if numero_processo:
            params['numeroProcesso'] = numero_processo
        if tribunal:
            params['tribunal'] = tribunal
        if classe:
            params['classe'] = classe
        if assunto:
            params['assunto'] = assunto
        if data_inicio:
            params['dataInicio'] = data_inicio
        if data_fim:
            params['dataFim'] = data_fim
        
        try:
            response = requests.get(
                f"{self.base_url}/processos",
                params=params,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Erro ao consultar API do DataJud: {str(e)}',
                'data': []
            }
    
    def get_process_details(self, processo_id: str) -> Dict:
        """
        Obtém detalhes de um processo específico
        
        Args:
            processo_id: ID do processo
            
        Returns:
            Dict com os detalhes do processo
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/processos/{processo_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Erro ao obter detalhes do processo: {str(e)}',
                'data': None
            }
    
    def get_process_movements(self, processo_id: str) -> Dict:
        """
        Obtém movimentações de um processo
        
        Args:
            processo_id: ID do processo
            
        Returns:
            Dict com as movimentações do processo
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/processos/{processo_id}/movimentacoes",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Erro ao obter movimentações do processo: {str(e)}',
                'data': []
            }
    
    def get_tribunals(self) -> Dict:
        """
        Obtém lista de tribunais disponíveis
        
        Returns:
            Dict com a lista de tribunais
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/tribunais",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Erro ao obter lista de tribunais: {str(e)}',
                'data': []
            }
    
    def get_process_classes(self) -> Dict:
        """
        Obtém lista de classes processuais
        
        Returns:
            Dict com a lista de classes processuais
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/classes",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Erro ao obter classes processuais: {str(e)}',
                'data': []
            }
    
    def get_process_subjects(self) -> Dict:
        """
        Obtém lista de assuntos processuais
        
        Returns:
            Dict com a lista de assuntos processuais
        """
        
        try:
            response = requests.get(
                f"{self.base_url}/assuntos",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': True,
                'message': f'Erro ao obter assuntos processuais: {str(e)}',
                'data': []
            }

