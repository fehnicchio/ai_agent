import os
import re
from dotenv import load_dotenv
from nlp_processor import NLPProcessor
from database import Database

class AIAgent:
    def __init__(self, db_config):
        self.nlp_processor = NLPProcessor()
        self.db = Database(db_config)
        self.schema_info = self._load_schema_info()
        self.max_results = int(os.getenv('MAX_RESULTS', 100))
    
    def _load_schema_info(self):
        """Obtém metadados do banco de dados para validação"""
        return {
            'tabelas': self.db.get_table_names(),
            'colunas': self.db.get_column_names()
        }
    
    def _validate_query(self, sql):
        """Valida se a query gerada é segura"""
        prohibited_keywords = ['insert', 'update', 'delete', 'drop', 'alter', 'truncate']
        if any(kw in sql.lower() for kw in prohibited_keywords):
            raise ValueError("Operação não permitida!")
        
        # Validação básica de tabelas/colunas
        for table in re.findall(r'FROM\s+(\w+)', sql, re.IGNORECASE):
            if table.lower() not in [t.lower() for t in self.schema_info['tabelas']]:
                raise ValueError(f"Tabela {table} não existe")
        
        return sql

    def ask(self, question):
        """Processa uma pergunta e retorna a resposta"""
        try:
            # Passo 1: Processamento de linguagem natural
            processed = self.nlp_processor.process(question)
            
            # Passo 2: Geração de SQL
            sql = self._generate_sql(processed)
            sql = self._validate_query(sql)
            
            # Passo 3: Executar consulta
            result = self.db.execute_query(sql)
            return result
        except Exception as e:
            return f"Erro: {str(e)}"

    def _generate_sql(self, processed_data):
        """Gera SQL baseado na análise da pergunta"""
        # SELECT clause
        if processed_data.get('aggregation'):
            select_clause = f"SELECT {processed_data['aggregation']['function']}({processed_data['aggregation']['column']})"
        else:
            select_clause = "SELECT *"
        
        # FROM clause
        table = processed_data.get('table', 'pedidos')
        from_clause = f" FROM {table}"
        
        # JOIN clause
        join_clause = ""
        if processed_data.get('join'):
            join = processed_data['join']
            join_clause = f" JOIN {join['table']} ON {join['on']}"
        
        # WHERE clause
        where_clause = ""
        if processed_data.get('conditions'):
            conditions = []
            for condition in processed_data['conditions']:
                col = condition['column']
                val = condition['value']
                op = condition.get('operator', '=')
                
                # CORREÇÃO IMPORTANTE: Referência correta para tabela de clientes
                if processed_data.get('join') and col in ['nome', 'estado']:
                    col = f"{processed_data['join']['table']}.{col}"
                elif col in ['nome', 'estado'] and not processed_data.get('join'):
                    # Força JOIN se necessário
                    if processed_data['table'] == 'pedidos':
                        join_clause = " JOIN clientes ON pedidos.cliente_id = clientes.id"
                        col = f"clientes.{col}"
                    elif processed_data['table'] == 'clientes':
                        col = f"clientes.{col}"
                
                if isinstance(val, str):
                    val = f"'{val}'"
                conditions.append(f"{col} {op} {val}")
            
            where_clause = " WHERE " + " AND ".join(conditions)
        
        # ORDER BY and LIMIT
        order_clause = f" ORDER BY {processed_data['order_by']}" if processed_data.get('order_by') else ""
        limit_clause = f" LIMIT {self.max_results}"
        
        return f"{select_clause}{from_clause}{join_clause}{where_clause}{order_clause}{limit_clause};"

# Execução principal
if __name__ == "__main__":
    from dotenv import load_dotenv
    import os
    
    # Carrega .env com encoding específico para Windows
    try:
        load_dotenv('.env', encoding='cp1252')  # Encoding comum no Windows
    except:
        load_dotenv('.env')  # Fallback
    
    db_config = {
        'host': os.getenv('DB_HOST'),
        'port': os.getenv('DB_PORT', 5432),
        'database': os.getenv('DB_NAME'),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD')
    }
    
    agent = AIAgent(db_config)
    
    print("=== Agente de IA para Consultas ao Banco de Dados ===")
    print("Digite sua pergunta (ou 'sair' para encerrar):")
    
    while True:
        question = input("\n> ")
        if question.lower() == 'sair':
            break
        
        response = agent.ask(question)
        
        if isinstance(response, list) and response:
            print("\nResultado:")
            for row in response:
                print(row)
        else:
            print(f"\n{response}")