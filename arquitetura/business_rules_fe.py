#################################################################################################################
# Aplicação: Extração de informações de banco de dados
# Autor    : Sandrerley Ramos Pires                                                                10/01/2025            
#            
# Finalidade:Esta aplicação tem como objetivo a inserção na base de conecimento de
#            um conjunto de regras de negócio. Essas regras de negócio serão postadas 
#            em uma coleção específica informada no arquivo de parâmetros que contém
#            as regras.
#
#            Este código trata a porção Front-End da aplicação. Deve ser executado 
#            em uma janela de comandos
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
def send_message(business_rules):
    API_URL = "http://localhost:8000/send"
    message = {
        "messagem":  0,
        "moment":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sender":   "business_rules_fe",
        "receiver": "business_rules_be",
        "control":  4,
        "content":   business_rules,
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
    parser = argparse.ArgumentParser(description="Criação de coleção com regras de negócio do sistema.")
    parser.add_argument("-j", default="D:/ebook10/sad/business_rules.json", help="Nome do arquivo Json com as regras de negócio.)")
    args = parser.parse_args()

    # Se pedido a recriaçãao, então deleta o banco de dados antigo
    print('Extraindo Regras de Negócio do arquivo:', args.j)
    response = send_message(args.j)
    
    # Laço de espera de resultado
    API_URL = "http://localhost:8000/finished/" + str(response.json())
    start_time = time.time()
    max_seconds = 60
    while time.time() - start_time < max_seconds:
        if requests.get(API_URL):
            break
        time.sleep(1)
        
    if time.time() - start_time < max_seconds:
        print('Geração de Regras de Negócio realizada com Sucesso.', time.time() - start_time, 'segundos de Execução')
