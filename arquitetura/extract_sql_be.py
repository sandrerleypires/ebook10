#################################################################################################################
# Aplicação: Chunk_from_book
# Autor     : Sandrerley Ramos Pires                                              10/11/2024            
#            
# Finalidade:Esta aplicação tem como objetivo a extração de informações de um banco de dados. Para tanto
#            recebe-se o nome do arquivo de parâmetros que localiza o BD, a query extratora e o padrão 
#            para a formação dos chunks. 
#
#            Este código trata a porção Back-End da aplicação. A implementação é chamada pelo controlador.
#
#            O objetivo da aplicação é apenas exemplificar formas de se resolver um problema. Não há
#            uma preocupação profunda com a completa correteza dela, podendo em entradas diferentes das
#            utilizadas neste curso, ocorrerem problemas de execução.
#
#################################################################################################################
import os
import json
from db_classes import connect_db, close_db
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

# Extrai a porção de loop de informações do template
def extract_loop_line(template):
    ini = template.find('<loop>') + 6
    linha_loop = ''
    if ini> 5: # Tem loop no template
       fim = template.find('<\\loop>')
       linha_loop = template[ini:fim]
       template   = template[:ini-6]
    return linha_loop, template

# Efetua as substituições no template ou nas loop_lines
def replace_chunk(df, template, tupla, seq):
    saida = template
    for col_name, col_type in df.dtypes.items():
        if col_type not in ['int8', 'int32', 'int64']:
            saida = saida.replace('<'+col_name+'>', str(tupla[col_name]))
        else:
            saida = saida.replace('<'+col_name+'>', str(tupla[col_name]))       
    return saida.replace('<#seq>', str(seq))
        
# Executa uma query SQL no banco de dados
def query_sql(bd, sql): 
    connection, cursor = connect_db(bd)
    df = pd.read_sql_query(sql, connection)
    close_db(connection)
    #print(bd, '\n', sql, '\n\n---->', df)
    return df  

# Efetua a inserção de um chunk na base de conhecimento
def insere_chunk(model, collection, id_chunk, chunk):
    r = collection.get(ids=[id_chunk])
    if r['documents'] == []:
        embedding = model.encode(chunk)
        collection.add(documents=[chunk], embeddings=[embedding],  ids=[id_chunk])
    else:
        print('já existe este id na base de conhecimento: ', r['documents']) 

def _extract_sql_be(nmsg, message):
    parm_file       =  message[0:message.find('@')] # obtem o nome do arquivo de parâmetros
    parm_collection = message[message.find('@')+1:] # obtem o nome da coleção a ser carregada

    if not os.path.exists(parm_file):
       resp = "O arquivo de parâmetros não existe:" + parm_file
       return nmsg, False, resp
    else:
        with open(parm_file, 'r', encoding='utf-8') as fp:
            parametros = json.load(fp)
            try:                
                sql = parametros['sql']                # Comando SQL para extração de dados do banco de dados         
                bd  = parametros['bd']                 # localização ODBC do banco de dados
                template = parametros['template']      # Template para geração do chunk
                origin =  parametros['origin']         # Identificação do tipo de informação extraída
                local_bd = parametros['local_bd']      # Local onde ficará a base de conhecimento
            except:
                resp = "Problema na obtenção dos parâmetros. Possível arquivo inválido."
                return nmsg, False, resp

    # Efetua a inicialização da coleção no Chromadb
    try:
        #Cria instância para acesso ao Chromadb
        chroma_client = chromadb.PersistentClient(local_bd)
        
        # Acessa a coleção, caso ela não exista, ela é criada.
        collection = chroma_client.get_or_create_collection(name=parm_collection)
        
        # Cria classe para cálculo de embeddings
        model = SentenceTransformer("all-MiniLM-L6-v2")
        
    except:
        resp = "Problema na criação da coleção. Confira instalação do Cromadb."
        return nmsg, False, resp    
    
    # Efetua a busca de dados no Banco de dados
    try:
        df = query_sql(bd, sql) 
    except:
        resp = "Problema na obtenção dos dados do bd. Confira arquivo de parâmetros."
        return nmsg, False, resp
    #
    # Percorre o retorno do banco de dados gerando os chunks e os embbedings do conteúdo
    #
    loop_line, template = extract_loop_line(template)
    #print('++', loop_line, template)
    id_before = ''
    chunk     = ''
    seq       = 1
    for i, tupla in df.iterrows():
        # Verifica se houve mudança de construtora
        if id_before != str(tupla['id']):
            # insere o chunk se ele estiver formado.
            if chunk !='':
                insere_chunk(model, collection, origin+id_before, chunk)
                chunk = ''
                
            # Gera a porção inicial do template
            chunk = replace_chunk(df, template, tupla, 0)
            id_before = str(tupla['id'])
            seq       = 1
    
        #Insere a porção repetitiva do chunk. Elementos de um mesmo id
        chunk += replace_chunk(df, loop_line, tupla, seq)
        seq   += 1
        
    # Após o término do laço, se houver algum chunk pendente, ele é gravado.
    if chunk !='':
        insere_chunk(model, collection, origin+id_before, chunk)
    
    # O encerramento da coleção e do Cliente e Feito pelo chromadb
    return nmsg, True, 'Query carregada na base de conhecimento. Coleção: ' + parm_collection
    
