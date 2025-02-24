#################################################################################################################
# Aplicação : gera_db - Gera o banco de dados para uso do gerenciador de mensagem.
#
# Autor     : Sandrerley Ramos Pires                                 05/12/2024            
#            
# Finalidade: Esta aplicação tem como objetivo oferecer a implementação de diversos
#             serviços básicos que são oferecidos para um banco de dados relacional.
#
#################################################################################################################
import sqlite3

# Cria o Banco de dados
def create_db(dbname):
    # Cria a estrutura de arquivo para que o sistema gerenciador de mensagem possa rodar.
    # Conectar ao banco de dados (cria o arquivo se ele não existir)
    connection = sqlite3.connect(dbname)
    close_db(connection)
    return connection

# encerra o uso do banco de dados
def close_db(connection):
    # Fechar a conexão
    connection.close()
    
def connect_db(dbname):
    # Conectar ao banco de dados (ou criar um novo arquivo)
    connection = sqlite3.connect(dbname)
    # Criar um cursor para executar comandos SQL
    cursor = connection.cursor()
    return connection, cursor

# Executa uma query no banco de dados, recebe o sql pronto
def query(dbname, sql): 
    connection, cursor = connect_db(dbname)
    cursor.execute(sql)
    tabela = cursor.fetchall()
    close_db(connection)
    return tabela

# Efetua a inserção de uma estrutura dict no BD, dada a tabela 
def insert_db(dbname, table_name, fields):
    connection, cursor = connect_db(dbname)
    try:
        columns = ', '.join(fields.keys())
        values = ''
        for v in fields.values():
            if type(v) is str:
                values += "'" + v + "'"      
            else:
                values += str(v)
            values += ', '  
        sql_cmd = "INSERT INTO %s ( %s ) VALUES ( %s )" % (table_name, columns, values[:-2])
        cursor.execute(sql_cmd)
        ultimo_id = cursor.lastrowid
        cursor.execute('commit;')
        close_db(connection)
        return int(ultimo_id)
    except Exception as e:
        close_db(connection)
        return e

# Efetua a inserção de uma estrutura dict no BD, dada a tabela 
def update_status(dbname, table_name, message, status):
    connection, cursor = connect_db(dbname)
    try:
        sql_cmd = "UPDATE message SET status = '" + status +"' where id = " + str(message)
        cursor.execute(sql_cmd)
        resp = cursor.rowcount # quantidade de linhas alteradas na tabela
        cursor.execute('commit;')
        close_db(connection)
        return int(resp)
    except Exception as e:
        print('is there an exception', e)
        close_db(connection)
        return -1
    
# Efetua a inserção da resposta na, dada a tabela 
def update_response(dbname, table_name, fields):
    connection, cursor = connect_db(dbname)
    try:
        sql_cmd = "UPDATE message SET status = 'R', response='" + fields['response'] +"' where id = " + str(fields['nmsg'])
        cursor.execute(sql_cmd)
        resp = cursor.rowcount # quantidade de linhas alteradas na tabela
        cursor.execute('commit;')
        close_db(connection)
        return int(resp)
    except Exception as e:
        print('is there an exception', e)
        close_db(connection)
        return -1
    
# Efetua a criação das tabelas do BD
def create_tables(cursor):
    # Criar a tabela de mensagens
    sql_cmd = """CREATE TABLE IF NOT EXISTS message (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 moment text not null, 
                 sender TEXT NOT NULL,
                 receiver TEXT NOT NULL,
                 control INTEGER,        
                 content TEXT NOT NULL,
                 response TEXT,
                 log     TEXT NOT NULL,
                 status  TEXT NOT NULL
    )"""
    r = cursor.execute(sql_cmd)
    return r
        
