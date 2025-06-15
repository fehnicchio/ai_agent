import psycopg2
import psycopg2.extras
import os
from urllib.parse import quote

class Database:
    def __init__(self, config):
        self.config = config
        self.connection = self._connect()
    
    def _connect(self):
        """Estabelece conexão com o banco de dados com tratamento de encoding"""
        try:
            # Codifica a senha para URL-safe
            password = quote(self.config['password'])
            
            conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                database=self.config['database'],
                user=self.config['user'],
                password=password,
                client_encoding='utf-8'
            )
            return conn
        except Exception as e:
            # Tenta conexão sem encoding forçado
            try:
                conn = psycopg2.connect(
                    host=self.config['host'],
                    port=self.config['port'],
                    database=self.config['database'],
                    user=self.config['user'],
                    password=self.config['password']
                )
                return conn
            except Exception as fallback_error:
                raise ConnectionError(f"Falha na conexão: {str(e)} | Fallback: {str(fallback_error)}")
    
    def execute_query(self, sql):
        """Executa uma query SQL e retorna resultados"""
        try:
            # Cria um novo cursor para cada query
            with self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute("ROLLBACK;")  # Reseta transação anterior
                cursor.execute(sql)
                if cursor.description:
                    return [dict(row) for row in cursor.fetchall()]
                return []
        except psycopg2.Error as e:
            # Fecha a conexão corrompida e cria uma nova
            self.connection.close()
            self.connection = self._connect()
            raise Exception(f"Erro SQL: {str(e)}")
    
    def get_table_names(self):
        """Obtém nomes das tabelas do banco"""
        sql = """
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        """
        return [row['table_name'] for row in self.execute_query(sql)]
    
    def get_column_names(self, table_name=None):
        """Obtém nomes das colunas do banco"""
        sql = """
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public'
        """
        if table_name:
            sql += f" AND table_name = '{table_name}'"
        return [row['column_name'] for row in self.execute_query(sql)]
    
    def close(self):
        """Fecha a conexão com o banco"""
        if self.connection:
            self.connection.close()