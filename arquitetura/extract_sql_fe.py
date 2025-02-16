#################################################################################################################
# Aplicação: Extração de informações de banco de dados
# Autor    : Sandrerley Ramos Pires                                                                10/01/2025            
#            
# Finalidade:Esta aplicação tem como objetivo a extração de informações de um banco de dados. Para tanto
#            recebe-se o nome do arquivo de parâmetros que localiza o BD, a query extratora e o padrão 
#            para a formação dos chunks. 
#
#            Este código trata a porção Front-End da aplicação. Deve ser executado em uma janela de comandos
#
#            O objetivo da aplicação é apenas exemplificar formas de se resolver um problema. Não há
#            uma preocupação profunda com a completa correteza dela, podendo em entradas diferentes das
#            utilizadas neste curso, ocorrerem problemas de execução.
#
#################################################################################################################
import argparse
import requests
from datetime import datetime
import time

# Relação de Livros a serem tratados
def send_message(parm_sql, colecao):
    API_URL = "http://localhost:8000/send"
    message = {
        "messagem":  0,
        "moment":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sender":   "extract_sql_fe",
        "receiver": "extract_sql_be",
        "control":  4,
        "content":   parm_sql+'@'+colecao,
        "log":      "False",
        "status":   "E"
        }
    response = requests.post(API_URL, json=message) 
    return response  
#
# Programa principal
#
if __name__ == "__main__":
    gerar = True
    
    # Criar o analisador de argumentos
    parser = argparse.ArgumentParser(description="Criação de coleção com informações de um banco de dados.")
    parser.add_argument("-j", default="D:/ebook10/sad/sad_sql.json", help="Nome do arquivo Json com os dados para extração.)")
    parser.add_argument("-c", default="sad_info", help="Nome da coleção da base de conhecimento que armazenará o resultado da extração.")
    args = parser.parse_args()

    # Se pedido a recriaçãao, então deleta o banco de dados antigo
    print('Extraindo do Banco de Dados. Parêmetros', args.j, ' para a Coleção: ', args.c)
    response = send_message(args.j, args.c)
    
    # Laço de espera de resultado
    API_URL = "http://localhost:8000/finished/" + str(response.json())
    start_time = time.time()
    max_seconds = 60
    while time.time() - start_time < max_seconds:
        if requests.get(API_URL):
            break
        time.sleep(1)
        
    if time.time() - start_time < max_seconds:
        print('Extraçao SQL concluída com Sucesso.', time.time() - start_time, 'segunds de Execução')


        