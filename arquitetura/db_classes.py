#################################################################################################################
# Aplicação : gera_db - Gera o banco de dados para uso do gerenciador de mensagem.
#
# Autor     : Sandrerley Ramos Pires                                 05/12/2024            
#            
# Finalidade: Esta aplicação tem como objetivo gera o banco de dados para que o 
#             gerenciador de mensagem. o Modo de uso da aplicação é:
#            
#             na linha de comando digite: python gera_db -r -dbname message.db 
#             onde, as opções:
#                "-dbname": É o nome do banco de dados a ser criado/recriado. O default é message.db
#                "-r" recria o banco de dados vazio, caso ele já exista
#
#################################################################################################################
import argparse
import os
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
    #print('Retorno da criação de tabelas:', r)
    return 

#
# Programa principal
#
if __name__ == "__main__":
    gerar = False
    
    # Criar o analisador de argumentos
    parser = argparse.ArgumentParser(description="Criação da Base de dados para o Gerenciador de Mensagem.")
    parser.add_argument("-dbname", default="message.db", help="Nome do banco de dados a ser criado)")
    parser.add_argument("-r", action="store_true", help="Caso já exista, o database será recriado.")
    args = parser.parse_args()

    # Se pedido a recriaçãao, então deleta o banco de dados antigo
    print('Criando o db', args.dbname, ' com a opção: ', args.r)
    if os.path.exists(args.dbname):
        if args.r:
            print("O banco de dados já existe. Excluindo-o...")
            os.remove(args.dbname)
            gerar = True
    else:
        gerar = True
    #
    # Cria o novo banco de dados se for necessário
    if gerar:
        create_db(args.dbname)
        connection, cursor = connect_db(args.dbname)
        create_tables(cursor)
        close_db(connection)
        