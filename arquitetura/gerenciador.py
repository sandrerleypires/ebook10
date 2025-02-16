#################################################################################################################
# Aplicação : gerenciador - administra o processo de comunicação entre  os diversos
#             móduloa do sistema.
#
# Autor     : Sandrerley Ramos Pires                                 05/12/2024            
#            
# Finalidade: Esta aplicação tem como objetivo administrar a troca de dados entre
#             os módulos da aplicação., por meio de seus serviços send (enviar
#             mensagens), o receive(Receber mensagem), o response(registrar resposta) 
#             e o finished,  É possível com ele acompanhar o trânsito completo 
#             de uma mensagem e tratar o log de fluxo de informações pelo sistema.
#
#################################################################################################################
from fastapi    import FastAPI, HTTPException
from pydantic   import BaseModel
from db_classes import insert_db, update_status, update_response, query
from datetime   import datetime

# Inicializa a task da FastAPI
app = FastAPI()
    
# Modelo de mensagem
class Message(BaseModel):
    #message: int     # Identificação única da mensagem
    moment: datetime # Momento em que a mensagem entrou no gerenciador.
    sender: str      # Módulo remetente da mensagem
    receiver: str    # Módulo destinatário da mensagem
    control: int     # Número de controle para identificação da mensagem 
    content: str     # Conteúdo da mensagem
    log: str         # Solicita S, ou não N, a gravação de log da mensagem
    status: str      # Status da Mensagem, S a Enviar,  D no destinatário,
                     #                     R respondida
# Modelo de mensagem de resposta
class Message_r(BaseModel):
    nmsg: int     # Identificação única da mensagem
    response: str    # Conteúdo da mensagem 
#
# Programa principal
#
if __name__ == "__main__":
    print('Gerenciador assíncrono de mensagens está no ar!')
    
#
# Porção relativa ao gerenciador ligado ao gerenciador de mensagem 
#
# Endpoint para enviar mensagens
@app.post("/send")
def send_message(message: Message):
    fields = {'moment':  str(message.moment),
              'sender':   message.sender,
              'receiver': message.receiver,
              'control':  message.control,
              'content':  message.content,
              'log':      message.log,
              'status':   message.status
        }
    resp = insert_db('message.db', 'message', fields)
    return resp

# Endpoint para buscar mensagens por destinatário
@app.get("/receive/{receiver}")
def receive_messages(receiver: str):
    sql = "SELECT * FROM message where receiver ='" + receiver + "' and status = 'E'"
    receiver_messages = query('message.db', sql)
    if len(receiver_messages)==0:
        raise HTTPException(status_code=404, detail="No messages found")
    else:
        for message in receiver_messages:
            num_update = update_status('message.db', 'message', message[0], 'D')
            if num_update < 1:
               print('problemas de atualização da mensagem', message)

    return {"messages": receiver_messages}

# Endpoint para buscar mensagens por destinatário
@app.post("/response")
def response_messages(message_r: Message_r):
    fields = {'nmsg':  message_r.nmsg, 'response': message_r.response}
    num_update = update_response('message.db', 'message', fields)
    if num_update < 1:
       resp = [False, 'problemas de atualização da mensagem'+ message_r]
    else:
       resp = [False, 'Mensagem encaminhada:' + str(num_update)]

    return resp

# Endpoint para buscar mensagens por destinatário
@app.get("/finished/{nmsg}")
def finished(nmsg: str):
    sql = f"SELECT * FROM message where id = {nmsg} and status = 'R'"
    messages = query('message.db', sql)
    if len(messages)>0:
        return messages[0][6]
    else:
        return "Nok"