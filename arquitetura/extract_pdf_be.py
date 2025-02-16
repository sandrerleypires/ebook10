#################################################################################################################
# Aplicação: virtual_assistant_be
# Autor     : Sandrerley Ramos Pires                                                  02/01/2025
#            
# Finalidade: Esta aplicação tem como objetivo receber uma pergunta do usuário e respondê-la de acordo
#             com o conteúdo extraído de um livro em PDF. Para tanto, executa os seguintes passos:
#             1) Calcula o Embedding da pergunta
#             2) busca subsídios para respondê-la na base de comhecimento 
#             3) monta o prompt para formalizar o pedido à LLM
#             4) recebe a resposta e a envia de volta ao cliente.
#
#             O objetivo da aplicação é apenas exemplificar formas de se resolver um problema. Não há
#             uma preocupação profunda com a completa correteza dela, podendo em entradas diferentes das
#             utilizadas neste curso, ocorrerem problemas de execução.
#
#################################################################################################################
import re
import os
import json
from extract_classes import Book_pdf, Linhas, Chunk, Gera_json
import chromadb
from sentence_transformers import SentenceTransformer

#
# Faz a extração dos dados do livro em PDF. Se tudo estiver certo, então gera coleção de conhecimento
#
def _extract_pdf_be(nmsg, message):
    # Efetua a leitura dos parâmetro informados pelo cliente
    print('--->', message)
    # obtem o nome do arquivo de parâmetros, do arquivo de saída e a opção de recriação da coleção
    [parm_file, parm_out_file, option] = message.split('@')
    livro =[]
    path_in = ""
    path_out = ""
    if not os.path.exists(parm_file):
       resp = "O arquivo de parâmetros não existe:" + parm_file
       return False, resp
    else:
        with open(parm_file, 'r', encoding='utf-8') as fp:
            parametros = json.load(fp)
            try:
                livro.append(parametros['title'])               # 0 - Título do livro
                livro.append(parametros['author'])              # 1 - Autor do Livro
                livro.append(parametros['edition'])             # 2 - Ediçao do livro
                livro.append(parametros['ISBN'])                # 3 - ISBN do Livro
                livro.append(parametros['year'])                # 4 - Ano de publicação da edição    
                livro.append(parametros['initial_page'])        # 5 - Página em que se localiza o primeiro tópico do livro.
                livro.append(parametros['discard'])             # 6 - Conteúdo fixo que será desconsiderado do livro. Ex. Titulo do livro em todas as páginas
                livro.append(parametros['character_end_topic']) # 7 - Indica se a numeração do tópico se encerra com ponto ou não. Ex. 1.2.1 ou 1.2.1.
                livro.append(True if parametros['jump_first_line']=='True' else False)     # 8 - Indica se salta a primeira linha de todas as páginas
                livro.append(True if parametros['can_jump_topic']=='True' else False)      # 9 - Efetua o tratamento de ausência de tópicos do livro na sequência deles 
                
                filename = parametros['file']                   # Nome do arquivo PDF que contém o livro           
                path_in  = parametros['path_in']                # Pasta onde estão os livros de origem.
                path_out = parametros['path_out']               # Pasta onde será gravado o Json do livro.
                
                local_bd = parametros['local_bd'] 
                collection_name = parametros['collection'] 
            except:
                resp = "Problema na obtenção dos parâmetros. Possível arquivo inválido."
                return False, resp
            
    Ok, resp_1, titulo = _livro_pdf2json(livro, filename, path_in, path_out, parm_out_file)
    if Ok:
        Ok, resp_2 = _json2collection(local_bd, collection_name, path_out, titulo)
        if Ok:
            return nmsg, Ok, resp_1 + resp_2
    else:
        return nmsg, Ok, resp_1
        
# Efetua a conversão de alivros em PDF para o formato Json    
def _livro_pdf2json(livro, filename, path_in, path_out, parm_out_file):
    # Se parâmetros estiverem corretos o livro será extraído
    fileout  = parm_out_file
    print('Início do processo de conversão do livro em PDF:', path_in + filename)
   
    # Cria uma instância da classe Book, fazendo a leitura e conversã do pdf para txt.
    book = Book_pdf(livro, path_in, filename)
        
    # Se terminou a conversão do livro, segue em frente
    if book.retorno == 0:
        # Cria uma instância das classes Book e Linhas, gerando uma lista com todas as linhas do livro
        linhas = Linhas(book)
        
        # Se terminou bem a geração de linhas, segue em frente
        if linhas.retorno==0:
            # Percorre as linhas e gera a tabela para formação do Json - Da melhor maneira possível, tenta definir capítulo e items no capítulo
            chunk = Chunk(linhas)
            tab_linha = chunk.gerar_chunk()
            print('Gerou ', len(tab_linha), 'chunks.')
        
            ## Se terminou de gera os chunks corretamente, segue em frente
            if len(tab_linha) > 0:
                # Percorre as linhas e gera a tabela para formação do Json - Da melhor maneira possível, tenta definir capítulo e items no capítulo
                gjson = Gera_json(linhas, tab_linha)
                livrox = gjson.gerar_json()              
                gjson.salva_json(livrox, path_out, fileout)    
            else:
                 return False, "Não gerou chunks corretamente.", ""
        else:
            return False, "Não gerou linhas corretamente. Erro:" + str(linhas.retorno),""
    else:
        return False, "Não gerou book corretamente. Erro:" + str(book.retorno), ""
   
    return True, 'Livro gerado no formato json:' + path_out+linhas.book.titulo, linhas.book.titulo




# Efetua a inserçao dos chunks do livro na coleção da base de conhecimento
def percorre_json(data, path="root"):
    list_chunks = []
    if isinstance(data, dict):  # Caso o item seja um dicionário, deve-se percorrer todos os itens do dict
        for key, value in data.items():
            current_path = f"{path}.{key}"
            list_chunks.append(["Key", current_path, type(value).__name__]) # salva a chave antes de percorrer subdict
            list_chunks += percorre_json(value, current_path)
    elif isinstance(data, list):  # Caso seja uma lista
        for index, value in enumerate(data):
            current_path = f"{path}[{index}]"
            list_chunks.append(["Index", current_path, type(value).__name__]) # salva o index antes de percorrer a lista
            list_chunks += percorre_json(value, current_path)
    else:  # Caso seja um valor atômico (int, str, float, etc.)
        list_chunks.append(["Leaf", path, data]) # salva o chunk na lista

    return list_chunks

def pesquisa(padrao, chunk):
    resp = re.search(padrao, chunk)
    return True if resp else False

#limpa os níveis do ID do chunk
def limpa(nivel, livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao):
    if nivel < 1: livro = ''
    if nivel < 2: capitulo = ''
    if nivel < 3: secao = ''
    if nivel < 4: subsecao = ''
    if nivel < 5: subsubsecao = ''
    if nivel < 6: subsubsubsecao = ''
    return livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao

# Gera o ID do chunk a partir da hierárquia do livro
def gera_id(livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao, paragrafo):
    id = livro
    if capitulo != '':
        id += ' - ' + capitulo
    if secao != '':
        id += ' - ' + secao
    if subsecao != '':
        id += ' - ' + subsecao
    if subsubsecao != '':
        id += ' - ' + subsubsecao
    if subsubsubsecao != '':
        id += ' - ' + subsubsubsecao
    id += ' - ' + paragrafo
    return id

# Efetua a inserção de um chunk na base de conhecimento
def insere_chunk(model, collection, id_chunk, chunk):
    r = collection.get(ids=[id_chunk])
    if r['documents'] == []:
        print('inclui ' + id_chunk)
        embedding = model.encode(chunk)
        collection.add(documents=[chunk], embeddings=[embedding],  ids=[id_chunk])
    else:
        print('já tem: ', r['documents']) 
        
def _json2collection(local_bd, collection_name, path_out, titulo):
    
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
        return False, resp      
    
    
    # Carregando e percorrendo um arquivo JSON
    with open(path_out+titulo, "r", encoding="utf-8") as file:
        dados_json = json.load(file)
    list_chunks = percorre_json(dados_json)
    
    print("Percorrendo a estrutura JSON:")
    livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao = limpa(0, '', '', '', '', '', '')
    for chunk in list_chunks:
        if chunk[0]=='Leaf':
            if   pesquisa(r'root.titulo', chunk[1]):           
                livro = chunk[2]          # título do Livro
                livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao = limpa(1, livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao)
            elif pesquisa(r'root.capitulo_\d+.numero:', chunk[1]):          
                capitulo = chunk[2]       # capítulo do Livro
                livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao = limpa(2, livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao)
            elif pesquisa(r'root.capitulo_\d+.section_\d+.\d+.titulo', chunk[1]):      
                secao = chunk[2]          # seção do Livro
                livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao = limpa(3, livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao)
            elif pesquisa(r'root.capitulo_\d+.section_\d+.\d+.section_\d+.\d+.\d+.titulo', chunk[1]):          # título do Livro
                subsecao = chunk[2]      # subseção do Livro
                livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao = limpa(4, livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao)
            elif pesquisa(r'root.capitulo_\d+.section_\d+.\d+.section_\d+.\d+.\d+.section_\d+.\d+.\d+.\d+.titulo', chunk[1]):     
                subsubsecao = chunk[2]     # subsubseção do Livro
                livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao = limpa(5, livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao)       
            elif pesquisa(r'root.capitulo_\d+.section_\d+.\d+.section_\d+.\d+.\d+.section_\d+.\d+.\d+.\d+.section_\d+.\d+.\d+.\d+.\d+.titulo', chunk[1]):
                subsubsubsecao = chunk[2]   # subsubsubseção do Livro
            elif pesquisa(r'texto.P_\d+', chunk[1]):
                 resp = re.search(r'texto.P_\d+', chunk[1])
                 id_chunk = gera_id(livro, capitulo, secao, subsecao, subsubsecao, subsubsubsecao, chunk[1][resp.start()+6:])
                 chunck_p = id_chunk + '\n' + chunk[2].replace('\n\n','\n')
                 insere_chunk(model, collection, id_chunk, chunck_p)
    
        # O encerramento da coleção e do Cliente e Feito pelo chromadb
    return True, 'Livro carregado na base de conhecimento. Coleção: ' + collection_name