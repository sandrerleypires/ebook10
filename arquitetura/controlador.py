#################################################################################################################
# Aplicação: aplicação controladora 
# Autor     : Sandrerley Ramos Pires                                              10/11/2024            
#            
# Finalidade: Esta aplicação tem como objetivo estabelecer uma comunicação com o
#             Gerenciador Assincrono de Mensagem e realizar as chamadas paralelas 
#             para as tasks do Back-End. 
#
#             Deve-se cadastrar nessa apricação a relação de serviços do Back-End   
#             que rodarão paralelamente.
#
#             O objetivo da aplicação é apenas exemplificar formas de se resolver um problema. Não há
#             uma preocupação profunda com a completa correteza dela, podendo em entradas diferentes das
#             utilizadas neste curso, ocorrerem problemas de execução.
#
#################################################################################################################
import asyncio
import requests
from extract_pdf_be import _extract_pdf_be
from extract_sql_be import _extract_sql_be 
from business_rules_be import _business_rules_be
from virtual_assistant_be import _virtual_assistant_be
#
# Tasks que tratam as tarefas oferecidas pela arquitetura
#
async def extract_pdf_be(nmsg, message):
    return _extract_pdf_be(nmsg, message)
     
async def extract_sql_be(nmsg, message):
    return _extract_sql_be(nmsg, message)

async def virtual_assistant_be(nmsg, message):
    return _virtual_assistant_be(nmsg, message)

async def business_rules_be(nmsg, message):
    return _business_rules_be(nmsg, message)
#
#  Função chamada automaticamente quando a tarefa termina.
#
def on_task_done(task):
    nmsg, Ok, response = task.result() 
    API_URL = "http://localhost:8000/response"
    message_r = {"nmsg": nmsg, "response": response}
    result = requests.post(API_URL, json=message_r) 
    
#
# Processa a recepção de uma mensagem
#
async def process_messages(API_URL):
    response = requests.get(API_URL)
    if response.status_code == 200:
        return True, response.json().get("messages", [])
    else:
        return False, response.json()
       
#
# Gerenciador de tarefas
#
async def main():
    # Relação dos serviços disponíveis de serem chamados
    servicos   = ['extract_pdf_be', 'extract_sql_be', 'virtual_assistant_be', 'business_rules_be']
    tasks_call = [extract_pdf_be,    extract_sql_be,   virtual_assistant_be, business_rules_be]
    
    # relação das tasks já executadas 
    task  = []
    ntask = 0
    
    # Cria laço eterno até definirem o fim do programa
    while True:
        for i, servico in enumerate(servicos):
            try:
                API_URL = "http://localhost:8000/receive/" + servico
                Ok, messages = await  asyncio.create_task(process_messages(API_URL))
                if Ok:
                    for message in messages:
                        # Dispara task de tratamento d mensagem
                        task.append(asyncio.create_task(tasks_call[i](message[0], message[5])))
                        task[ntask].set_name(servico)
                        
                        # Adiciona callbacks para serem executados quando cada tarefa terminar
                        task[ntask].add_done_callback(on_task_done)                      
                        ntask += 1 
                    await asyncio.gather(*task)
                    task  = []
                    ntask = 0                
            except:
                continue
        await asyncio.sleep(1)      # Aguarda um tempo (1s) para verificar mensagens novamente

# Ativa a task controladora do Back-End
if __name__ == "__main__":
    asyncio.run(main())
