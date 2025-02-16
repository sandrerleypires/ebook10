#################################################################################################################
# Aplicação : bd.py - Gera o banco de dados para uso do gerenciador de mensagem.
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
from db_classes import create_db, connect_db, create_tables, close_db

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
        