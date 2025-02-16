#################################################################################################################
# Aplicação: bussines_rules_be
# Autor     : Sandrerley Ramos Pires                                              01/02/2025            
#            
# Finalidade:Esta aplicação tem como objetivo a inserção na base de conecimento de
#            um conjunto de regras de negócio. Essas regras de negócio serão postadas 
#            em uma coleção específica informada no arquivo de parâmetros que contém
#            as regras.
#
#            Este código trata a porção Back-End da aplicação. A implementação
#            é chamada pelo controlador.
#
#            O objetivo da aplicação é apenas exemplificar formas de se resolver um problema. Não há
#            uma preocupação profunda com a completa correteza dela, podendo em entradas diferentes das
#            utilizadas neste curso, ocorrerem problemas de execução.
#
#################################################################################################################
import os
import json
import chromadb
from sentence_transformers import SentenceTransformer

# Efetua a inserção de um chunk na base de conhecimento
def insere_chunk(model, collection, id_chunk, chunk):
    r = collection.get(ids=[id_chunk])
    if r['documents'] == []:
        embedding = model.encode(chunk)
        collection.add(documents=[chunk], embeddings=[embedding],  ids=[id_chunk])
    else:
        print('já existe este id na base de conhecimento: ', r['documents']) 

def _business_rules_be(nmsg, message):
    parm_file       =  message                                 # obtem o nome do arquivo de parâmetros

    if not os.path.exists(parm_file):
       resp = "O arquivo de parâmetros não existe:" + parm_file
       return nmsg, False, resp
    else:
        with open(parm_file, 'r', encoding='utf-8') as fp:
            parametros = json.load(fp)
            try:  
                local_bd = parametros['local_bd']              # Local onde ficará a base de conhecimento                
                collection_name = parametros['collection']     # Nome da coleção da base de conhecimento        
                business_rules = parametros['rules']           # Relação das regras de negócio             
            except:
                resp = "Problema na obtenção dos parâmetros. Possível arquivo inválido."
                return nmsg, False, resp

    # Efetua a inicialização da coleção no Chromadb
    try:
        #Cria instância para acesso ao Chromadb
        chroma_client = chromadb.PersistentClient(local_bd)
        
        # Acessa a coleção, caso ela não exista, ela é criada.
        collection = chroma_client.get_or_create_collection(name=collection_name)
        
        # Cria classe para cálculo de embeddings
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
    except:
        resp = "Problema na criação da coleção. Confira instalação do Cromadb."
        return nmsg, False, resp    
    #
    # Percorre o retorno do banco de dados gerando os chunks e os embbedings do conteúdo
    #
    origin = 'business rules'
    for rule in business_rules:
        # Verifica se houve mudança de construtora
        insere_chunk(model, collection, origin+rule['name'], rule['rule'])  
    # O encerramento da coleção e do Cliente e Feito pelo chromadb
    return nmsg, True, 'Query carregada na base de conhecimento. Coleção: ' + collection_name
