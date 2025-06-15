import spacy
import re
from spacy.lang.pt import Portuguese

class NLPProcessor:
    def __init__(self):
        try:
            self.nlp = spacy.load("pt_core_news_sm")
            print("Modelo de português carregado com sucesso!")
        except OSError:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                print("Usando modelo em inglês como fallback")
            except:
                self.nlp = Portuguese()
                print("Usando modelo básico sem recursos avançados")
        
        self.keywords = {
            'quantos': {'type': 'aggregation', 'function': 'COUNT', 'column': '*'},
            'conte': {'type': 'aggregation', 'function': 'COUNT', 'column': '*'},
            'soma': {'type': 'aggregation', 'function': 'SUM'},
            'total': {'type': 'aggregation', 'function': 'SUM'},
            'média': {'type': 'aggregation', 'function': 'AVG'},
            'máximo': {'type': 'aggregation', 'function': 'MAX'},
            'mínimo': {'type': 'aggregation', 'function': 'MIN'},
            
            'cliente': {'type': 'table', 'value': 'clientes'},
            'clientes': {'type': 'table', 'value': 'clientes'},
            'pedido': {'type': 'table', 'value': 'pedidos'},
            'pedidos': {'type': 'table', 'value': 'pedidos'},
            'compra': {'type': 'table', 'value': 'pedidos'},
            'compras': {'type': 'table', 'value': 'pedidos'},
            
            'recente': {'type': 'order', 'value': 'DESC', 'column': 'data_pedido'},
            'recentes': {'type': 'order', 'value': 'DESC', 'column': 'data_pedido'},
            'novo': {'type': 'order', 'value': 'DESC', 'column': 'data_pedido'},
            'novos': {'type': 'order', 'value': 'DESC', 'column': 'data_pedido'},
            'antigo': {'type': 'order', 'value': 'ASC', 'column': 'data_pedido'},
            'antigos': {'type': 'order', 'value': 'ASC', 'column': 'data_pedido'},
            'maior': {'type': 'order', 'value': 'DESC', 'column': 'valor'},
            'menor': {'type': 'order', 'value': 'ASC', 'column': 'valor'},
        }
        self.max_results = 100
    
    def process(self, question):
        """Analisa a pergunta e extrai componentes para SQL"""
        doc = self.nlp(question.lower())
        result = {
            'table': None,
            'conditions': [],
            'aggregation': None,
            'join': None,
            'order_by': None
        }
        
        # 1. Identificar palavras-chave
        for token in doc:
            token_text = token.text.lower()
            if token_text in self.keywords:
                kw_info = self.keywords[token_text]
                
                if kw_info['type'] == 'table':
                    result['table'] = kw_info['value']
                
                elif kw_info['type'] == 'aggregation':
                    result['aggregation'] = {
                        'function': kw_info['function'],
                        'column': kw_info.get('column', self._find_aggregation_column(doc))
                    }
                
                elif kw_info['type'] == 'order':
                    result['order_by'] = kw_info.get('column', 'data_pedido') + " " + kw_info['value']
        
        # 2. Fallback para tabela padrão se não identificada
        if not result['table']:
            if any(token.text in ['pedido', 'pedidos', 'compra', 'compras'] for token in doc):
                result['table'] = 'pedidos'
            elif any(token.text in ['cliente', 'clientes'] for token in doc):
                result['table'] = 'clientes'
            else:
                result['table'] = 'pedidos'
        
        # 3. Extrair entidades e padrões
        # Estados por sigla (regex)
        state_pattern = r'\b(AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO)\b'
        for match in re.finditer(state_pattern, question, re.IGNORECASE):
            result['conditions'].append({
                'column': 'estado',
                'value': match.group().upper()
            })
        
        # Estados por nome completo
        state_map = {
            'são paulo': 'SP',
            'rio de janeiro': 'RJ',
            'minas gerais': 'MG',
            'paraná': 'PR',
            'parana': 'PR',
            'bahia': 'BA',
            'rio grande do sul': 'RS',
            'santa catarina': 'SC',
            'goiás': 'GO',
            'goias': 'GO'
        }
        
        # Entidades do spaCy
        for ent in doc.ents:
            if ent.label_ == 'LOC':
                state_lower = ent.text.lower()
                # Verifica se é um estado completo
                if state_lower in state_map:
                    result['conditions'].append({
                        'column': 'estado',
                        'value': state_map[state_lower]
                    })
            
            # Nomes de pessoas
            elif ent.label_ == 'PER':
                result['conditions'].append({
                    'column': 'nome',
                    'value': ent.text,
                    'operator': 'ILIKE'
                })
            
            # Datas/Anos
            elif ent.label_ == 'DATE' and re.match(r'\d{4}', ent.text):
                column = 'data_pedido' if result['table'] == 'pedidos' else 'data_cadastro'
                result['conditions'].append({
                    'column': column,
                    'value': f"{ent.text}-01-01",
                    'operator': '>='
                })
                result['conditions'].append({
                    'column': column,
                    'value': f"{ent.text}-12-31",
                    'operator': '<='
                })
        
        # 4. Detectar relações entre tabelas
        if (any(cond['column'] in ['nome', 'estado'] for cond in result['conditions']) or
            'clientes' in question or 'pedidos' in question):
            if result['table'] == 'pedidos':
                result['join'] = {
                    'table': 'clientes',
                    'on': 'pedidos.cliente_id = clientes.id'
                }
            elif result['table'] == 'clientes':
                result['join'] = {
                    'table': 'pedidos',
                    'on': 'clientes.id = pedidos.cliente_id'
                }
        
        # 5. Detectar números para limites
        for token in doc:
            if token.like_num and token.text.isdigit():
                self.max_results = int(token.text)
        
        return result
    
    def _find_aggregation_column(self, doc):
        """Encontra a coluna para agregação baseada no contexto"""
        for token in doc:
            token_text = token.text.lower()
            if token_text in ['pedidos', 'compras', 'vendas']:
                return 'id'
            if token_text in ['valor', 'preço', 'total']:
                return 'valor'
            if token_text in ['quantidade', 'itens']:
                return 'quantidade'
        return '*'