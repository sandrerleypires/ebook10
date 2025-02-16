#################################################################################################################
# Aplicação: Chunk_from_book
# Autor    : Sandrerley Ramos Pires                                              10/11/2024            
#            
# Finalida:  Esta aplicação tem como objetivo a extração de informações de um livro em formato 
#            PDF. Considerando que a organização de um material bibliográfico envolve inúmeros
#            formatos, esta aplicação atua em livros que possuem suas seções numeradas por pelo
#            seguinte padrão: "1.1 assunto", "1.3.1 título", "3.4.2.1 subsubtópico" etc. a 
#            primeira numeração indica o capítulo e as demais os sópicos e subtópicos que organiza 
#
#            a distribuição do conteúdo do livro.
#            Para a formação de chunks, utilizou-se a strutura de ópicos do livro e, ainda, a separação
#            do texto por parágrafos.
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
def send_message(parametros_json, outfile, option):
    API_URL = "http://localhost:8000/send"
    message = {
        "messagem":  0,
        "moment":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "sender":   "extract_pdf_fe",
        "receiver": "extract_pdf_be",
        "control":  3,
        "content":  parametros_json + '@' + outfile + '@' + option,
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
    parser = argparse.ArgumentParser(description="Criação de arquivo JSON a partir de Livro em formato PDF.")
    parser.add_argument("-j", default="D:/ebook10/chatbot/extract_pdf.json", help="Nome do arquivo Json com os dados para conversão.)")
    parser.add_argument("-o", default="", help="Nome do arquivo de saída.")
    parser.add_argument("-r", default="", help="Se esta opção é informada, a coleção é recriada.")
    args = parser.parse_args()

    # Se pedido a recriaçãao, então deleta o banco de dados antigo
    print('Convertendo o arquivo', args.j, '. Saída Explícita para:', args.o,', com a opção: ', args.r)
    response = send_message(args.j, args.o, args.r)
    
    # Laço de espera de resultado
    API_URL = "http://localhost:8000/finished/" + str(response.json())
    start_time = time.time()
    max_seconds = 30
    while time.time() - start_time < max_seconds:
        if requests.get(API_URL):
            break
        time.sleep(1)
        
    if time.time() - start_time < max_seconds:
        print('Conversão concluída com Sucesso.', time.time() - start_time, 'segunds de Execução')


        