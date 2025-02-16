#################################################################################################################
# Aplicação: Classes Extrator de Conteúdo - Livros em PDF
# Autor    : Sandrerley Ramos Pires                                              10/11/2024            
#            
# Finalida:  Este arquivo contém as classes auxiliares que são necessárias à implementação 
#            da funcionalidade de extração de conteúdo de livros em formato PDF. 
#            
# Restrições: 
#    1) Considerando que a organização de  um material  bibliográfico envolve inúmeros formatos,
#       esta aplicação atua em livros que possuem as suas seções numeradas pelo seguinte padrão:
#       "1.1 assunto", "1.3.1 título", "3.4.2.1 subsubtópico" etc.  A primeira numeração indica 
#       o capítulo e as demais os tópicos e subtópicos que organiza distribuição do conteúdo do 
#       livro.
#
#    2) O tipo de livro tratado aqui são os ebooks referentes ao curso de especialização.
#       Não há garantias de que este código funcione com outros tipos de livros em PDF.
#
#################################################################################################################

#
# Efetua a leitura do Livro em formato PDF, converte para texto e limpa alguns ruídos no texto.
#
#  Observação: Esta classe foi projetada com o objetivo de isolar o pacote de conversão PDF para texto.
#              Para os objetivos desta aplicação, o pacote pdftotext foi utilizado, mas existem diversos
#              outros que podem ser utilizados, dependendo da complexidade do problema tratado.
#
import pdftotext
class Book_pdf:
    def __init__(self, livro, path, filename):
        self.titulo           = livro[0]
        self.autor            = livro[1]
        self.edicao           = livro[2]
        self.ISBN             = livro[3]
        self.ano              = livro[4]
        
        # Indicadores para facilitar a exploração do livro
        self.inicio_conteudo  = livro[5]           # Página em que se inicia o conteúdo
        self.texto_a_saltar   = livro[6].lower()   # Indicaum trecho de texto ser desprezado.
        self.pula_linha_1     = livro[8]           # Indica se é ou não para pular a primeira linha
        self.fim_topico       = livro[7]           # Indica se a numeração do tópico se encerra com ponto ou não. Ex. 1.2.1 ou 1.2.1.
        self.dobraTopico      = livro[9]           # Considera a possibilidade de haver falhas na sequência dos tópicos do livro
        
        # propriedades para a implementação da classe
        self.i                = 0                  # Índice para percorrer o texto do livro
        self.retorno          = 0                  # 0: Ok, 1: Arquivo não encontrado, 2: outros
        self.page_content     = ''                 # Contém o texto do livro
        self.gera_texto(path, filename)            # Função que obtém od dados do livro 

    # Retorna o conteúdo do livro no formato txt, e também o tamanho do texto lido
    def get_page_content(self):
        return self.page_content
    def get_tam_texto(self):
        return len(self.page_content)

    #Retorna o status da classe. Tudo bem ou o código de erro.
    def get_retorno(self):
        return self.retorno

    #Retorna os conteúdos de cabeçalho e rodapé
    def get_texto_a_saltar(self):
        return self.texto_a_saltar

    # Efetua a troa de caracteres indesejados no texto (Ocorre em algumas conversões pdf --> txt)
    def limpa(self):
        inn = ['c ¸ ˜o', ' ˆa', '´ı', 'c ¸ ˜a', ' ´a', ' ´ı', ' ´e', 'ˆo', ' ˜a', ' ´o', 'c ¸', ' ˆe', '´a', '´e', ' ¨u', '�', '�', '\x08', '■ '] 
        out = [    'çõ',   'â',  'í',     'çã',   'á',   'í',   'é',  'ô',   'ã',   'ó',   'ç',   'ê',  'á',  'é',   'ü',  ' ',  ' ', '', '' ]
        i   = 0
        while i < len(inn):
            self.page_content = self.page_content.replace(inn[i], out[i])
            i+=1
    #
    # Efetua de leitura de pdf e montagem do txx
    def gera_texto(self, path, file):
        # Abre o arquivo pdf, verificando se ele existe
        try:
            pdf_file = open(path + file, 'rb')
        except OSError:
            print('Arquivo não existe:', path + file)
            self.retorno = 1
            return 
            
        # Le todas as páginas do arquivo PDF
        pdf               = pdftotext.PDF(pdf_file, physical=True)
        self.page_content = ''
        pag               = 0 
        ip                = 0        
        for page in pdf:
            # Verifica se é para elimina a primeira linha
            if self.pula_linha_1:    # Pula a primeira linha, caso tenha sido determinado
                ip = page.find('\n')
                if ip < 0:
                    ip = 0
           
            # Marca o número da página no texto.
            pag += 1
            self.page_content += '#@&' + str(pag) + '\n'
            if len(page) > 200:
                self.page_content += page[ip:].replace('\r','').replace('capitulo','capítulo').replace('sumario','sumário').replace('Capitulo','capítulo').replace('Sumario','sumário')  
        
        self.number_of_pages   = len(pdf)
        print('Número de páginas lidas: ', self.number_of_pages)
    
        # Preparação final do texto lido.
        self.limpa()
        
        
       
        
# 
#  Esta classe obtem o texto bruto da classe Book e o separa em linhas, com informação da
#  página. O objetivo é colocar o texto em um formato mais agradável para a manipulação.
#
class Linhas:
    
    def __init__(self, book):
        self.book    = book          # Classe Book que contém o conteúdo do livro
        self.pag     = 0             # Página corrente do Livro
        self.linhas  = []            # Relação de linhas do livro
        self.pag_lin = []            # Página do livro relativa a linha
        self.lin     = 0             # Linha corrente do livro que está sendo processada
        self.retorno = 0             # 0: Ok, 1: Texto vazio, 2: linha muito longa , 3: outros
        # Gera a representação do livro em linhas
        self.gera_linhas()           # Gera lista com o as linhas do texto
        
    # Funções de interface com o índice da lista de linhas
    def get_lin(self):
        return self.lin
    def set_lin(self, lin):
        self.lin = lin        
    def inc_lin(self):
        self.lin += 1
        
    # Funções de interface com a lista de linhas    
    def get_pag_lin(self, i):
        return self.pag_lin[i]
    def get_linha(self, i):
        return self.linhas[i]
    def get_linha(self):
        return self.linhas[self.lin]        
    def get_qt_lin(self):
        return len(self.linhas)        # Retorna a quantidade de linhas no livro

    #Retorna o status da classe. Tudo bem ou o código de erro.
    def get_retorno(self):
        return self.retorno 
    
    # Separa o bloco com todo o texto em uma lista de linhas
    def gera_linhas(self):
        # Verifica se o conteúdo do livro é desprezível. Possível erro de leitura. Nesse caso encerra e informa o erro
        if len(self.book.get_page_content()) < 10:
            self.retorno = 1
            return

        # Vai tratar a separção de linhas
        pag = 0
        pf  = -1
        fim = False
    
        # percorre o texto gerando as linhas do livro
        while not fim:        
            # Obtém a próxima linha
            pi = pf + 1
            pf = self.book.get_page_content().find('\n', pi)
            #print(self.book.get_tam_texto(), pi, pf, self.book.get_page_content()[pi:pf].lstrip().strip()) 

            # verifica se terminou as linhas a serem interpretadas    
            if (self.book.get_tam_texto()-pf) < 10:
                fim = True
                break                                # Força o encerramento do laço

            # Analisa a possibilidade de ter alcançado o fim do livro
            if pf == -1:
                if abs(pag - self.book.number_of_pages) < 2:    # Confirma se é fim de livro
                    self.linhas.append(self.book.get_page_content()[pi:].lstrip())
                    self.pag_lin.append(pag)       
                    break                             # Força o encerramento do laço
                    
            # Monta a linha a partir dos limites e verifica se existe uma emenda com a próxima linha
            linha = self.book.get_page_content()[pi:pf].lstrip().strip()
            
            # Identifica o número da página do livro referente às linhas da próxima página. Simbologia definida para tratar número de página
            if linha.find('#@&') == 0:
                pag = int(linha[3:len(linha)])
                continue
                
            # Despreza as linhas que sejam muito pequena. No caso, menos de 5 caracteres
            if len(linha) < 4:
                continue

            # Trata caso a linha contenha o trecho indicativo de salto de linha
            if linha.find(self.book.get_texto_a_saltar()) > -1:
                 continue

            # Insere a linha na tabela de linhas e páginas
            self.linhas.append(linha)
            self.pag_lin.append(pag)
            
        print('Número de linhas  criadas: ', self.get_qt_lin())
    #
    # Função auxiliar que imprime o conteúdo das linhas do livro. 
    # Parâmetros: Linha inicial e quantidade de linhas
    def prt_linhas(self, ini, qtlin):
        # Só para mostrar o intervalo informado de linhas
        k = ini
        print(qtlin, 'linhas', ini, 'até', ini+qtlin, 'das', len(self.linhas), 'linhas carregadas.')
        while k < ini + qtlin:
            print(k, '---> ',  self.pag_lin[k],  self.linhas[k])
            k += 1
        return        
    
# 
#  Esta classe visa  gerar um texto estruturado  pelos tópicos do livro. a ideia é gerar uma
#  hierarquia, onde cada parágrafo possa ser identificado pelo capitulo, seções e subseções,
#  faciltando o processo de indexação.
#
import re
class Chunk:
    def __init__(self, linhas):
        self.linhas  = linhas        # Classe linhas que contém as linhas do livro
  
    #
    # Funções de preparação das linhas pela localização dos itens do índice
    #
    def inicio_conteudo(self, pag):
        lin = 0
        while self.linhas.get_pag_lin(lin) < pag:
            lin += 1
        return lin
    
    def prox_itens(self, item):
        final = '.' if self.linhas.book.fim_topico=='.' else ''
        items = [item.strip() + ('.1' if self.linhas.book.fim_topico==' ' else '1.')]
        nums = item.split('.')
        tam_num = len(nums)
    
        for k in range(tam_num-1, -1, -1):
            if nums[k]=='':
                continue
            it = ".".join(nums[0:k])
            it = it + ("." if it!='' else '') + str(int(nums[k])+1) + ('.1' if k==0 else '') + final
            items.append(it)
    
        # Dobra a tabela para obter dobraTopico
        if self.linhas.book.dobraTopico:
            newitens = []
            for item in items:
                ind = -2 if final == '.' else -1
                prox_item = item[0:ind] + str(int(item[ind]) + 1) + final
                newitens.append(prox_item)
            prox_item = str(int(item[0]) + 1) + item[1:]
            newitens.append(prox_item)
            for item in newitens:
                items.append(item)
                
        return items
    
    def Eh_topico(self, linha, item_atu):
    
        if self.linhas.book.fim_topico=='.':
            padrao = r'\d+(\.\d+)*\.'
        else:
            padrao = r'\d+(\.\d+)*\ '
            
        resp   = re.search(padrao, linha)
    
        # Não encontrou na linha
        if resp == None:
            return False, '-1'
    
        # Não está na primeira posiçao da linha
        if resp.span()[0]!=0:
            return False, '-2'
    
        # obtém o índice corrente
        item = linha[0:resp.span()[1]].strip()
    
        # Verifica se o item possui '.' em seu corpo. Se não tiver, despreza.
        if item.find('.')== -1:
            return False, '-3'
            
        # Verifica se existe mais tópicos na linha. Se tiver despreza
        resp   = re.search(padrao, linha[resp.span()[1]:])
        if resp != None and resp.group().find('.')!=-1:
            return False, '-4'
    
        # analisa lógica da sequência. O item encontrado tem que ser um dos possíveis índices
        items = self.prox_itens(item_atu)
        if item not in items:
            print('Problema com os índices. Encontrou um tópico que não estava na tabela. \n', \
                  self.linhas.get_pag_lin(self.linhas.get_lin()), self.linhas.get_lin(), linha, '\n',item, '\t\t', item_atu,  items, '\n')
            return False, '-5'
            
        # Se aprovados nos testes anteriores então é Tópico
        return True, item
    
    # Prepara o início de um novo capítulo
    def gerar_chunk(self,):
        tab_linha = []
        capitulo  = ''
        topico    = ''
        #livro_nome = self.linhas.book.titulo 
        self.linhas.set_lin(self.inicio_conteudo(self.linhas.book.inicio_conteudo))
        final = '.' if self.linhas.book.fim_topico=='.' else ''
        item_atu = '1' + final
        while self.linhas.get_lin() < self.linhas.get_qt_lin():
            #print(self.linhas.get_linha(), '<---->', item_atu)
            # Processa a linha
            eh_top, item =  self.Eh_topico(self.linhas.get_linha(), item_atu)
            if eh_top:
                capitulo = self.linhas.get_linha()[0:self.linhas.get_linha().find('.')]
                topico   = item        
                if item_atu != item:
                    item_atu = item
    
            # gera os parágrafos para o json    
            if item != '-4' and item_atu != ('1'+final):
                tab_linha.append([self.linhas.get_pag_lin(self.linhas.get_lin()), str(self.linhas.get_lin()), capitulo, topico,  self.linhas.get_linha()])    
            self.linhas.inc_lin()              
            
            #if self.linhas.get_lin() > 500:
            #   break
                
        return tab_linha
    
    
    
#
# Classe responsável por formatar o arquivo JSON
#    
import json
class Gera_json:
    def __init__(self, linhas, tab_linha):
        self.linhas    = linhas    # Classe linhas que contém as linhas do livro
        self.tab_linha = tab_linha

    
    # Prepara o início de um novo capítulo
    def zera_cap(self,linha):
        sections = []    
        item_atu = []
        textos   = []    
        
        # Abre novo capítulo
        cap_dict = {'capitulo_' + linha[2]: {'numero:':linha[2], 'titulo':'', 'pagina':linha[0], 'linha': linha[1]}}
        cap_atu  = linha[2]
       
        # gera a nova seção do capítulo
        sections.append({'section_' + linha[3]: {'numero:':linha[3], 'titulo':linha[4], 'pagina':linha[0], 'linha': linha[1]}})
        item_atu.append(linha[3])
        return cap_dict, sections, cap_atu, item_atu, textos

    # Percorre as linhas e gera o Json - Da melhor maneira possível
    def conteudo(self, textos):
        texto  = {}
        txt = ''
        par = 1
        for linha in textos:
            if linha=='':
                continue
                
            # Trata da extração de figuras do texto
            padrao = 'Figura \d* - [\w|\s|,]*'
            resp   = re.search(padrao, linha)
            if resp:
                if txt != '':
                    texto.update({'P_'+ str(par): txt})
                    txt = ''
                    par += 1
                num  = re.search('\d* -', linha)
                texto.update({'Fig_'+ linha[num.span()[0]:  num.span()[1]-1]: \
                              {'num':linha[num.span()[0]:  num.span()[1]-1], \
                               'texto':linha[num.span()[1]: resp.span()[1]]} \
                             })
            else:
                # Trata linha de texto
                txt = txt + linha.replace("'", '"') + '\n'
                if (len(linha) < 50 and linha[-1] in ['.', '?', ':']) or \
                    len(linha) < 30:
                    texto.update({'P_'+ str(par): txt})
                    txt = ''
                    par += 1
            
        if txt!='':
            texto.update({'P_'+ str(par): txt})
        return texto
    
    def gerar_json(self):
        # Percorre as linhas e gera a estrutura json
        livro   = {'titulo': self.linhas.book.titulo}
        first   = True
        final = '.' if self.linhas.book.fim_topico=='.' else ''
        for linha in self.tab_linha:
            # Prepara o primeiro capítulo e primeira seção
            if first:
                first= False
                cap_dict, sections, cap_atu, item_atu, textos = self.zera_cap(linha) 
        
            # Obtém os niveis do item corrente e dos anteriores
            item   = item_atu[len(item_atu)-1]
            nivel  = item.count('.') - 1 - (1 if final=='.' else 0)
            nivnew = linha[3].count('.') - 1 - (1 if final=='.' else 0)
            
            # verifica se mudou o capítulo
            if cap_atu != linha[2]:
                # carrega o texto da seção corrente
                sections[nivel]['section_' + item].update({'texto':self.conteudo(textos)})
                while nivnew <= nivel:
                    if nivel==0:
                        cap_dict['capitulo_' + cap_atu].update(sections[nivel])
                        break
                    else:
                        sections[nivel-1]['section_'+ item_atu[len(item_atu)-2]].update(sections[nivel])
                        
                    del sections[nivel]
                    nivel -= 1
                    del item_atu[len(item_atu)-1]
                    textos = []
        
                livro.update(cap_dict)
                # Prepara um novo capítulo
                cap_dict, sections, cap_atu, item_atu, textos = self.zera_cap(linha) 
                # Obtém o item corrente
                item  = item_atu[len(item_atu)-1]
                nivel = item.count('.') 
        
            # Verifica se mudou de tópico, se mudou avalia o procedimento ocorrido e atua
            if item != linha[3]: 
                # trata a mudança de tópico para outro de mesmo nível
                if nivnew == nivel: # O nível anterior e o atual são os mesmos.
                    # carrega o texto da seção corrente       
                    sections[nivel]['section_' + item].update({'texto':self.conteudo(textos)})
                    if nivel==0:
                        cap_dict['capitulo_' + cap_atu].update(sections[nivel])
                    else:
                        sections[nivel-1]['section_'+ item_atu[len(item_atu)-2]].update(sections[nivel])
                    del sections[nivel]
                    nivel -= 1
                    del item_atu[len(item_atu)-1]
                    textos = []
        
                # trata a mudança de tópico para um novo nível menor
                elif nivnew < nivel:
                    # carrega o texto da seção corrente       
                    sections[nivel]['section_' + item].update({'texto':self.conteudo(textos)})
                    while nivnew <= nivel:
                        if nivel==0:
                            cap_dict['capitulo_' + cap_atu].update(sections[nivel])
                        else:
                            sections[nivel-1]['section_'+ item_atu[len(item_atu)-2]].update(sections[nivel])
                        del sections[nivel]
                        nivel -= 1
                        del item_atu[len(item_atu)-1]
                        item = item_atu[len(item_atu)-1] if (len(item_atu)-1) >=0 else ''
                        textos = []
        
                # trata a mudança de tópico para um novo nível menor
                elif nivnew > nivel:
                     # carrega o texto da seção corrente    
                     if len(item_atu) > 0:
                         sections[nivel]['section_' + item].update({'texto':self.conteudo(textos)})
                    
                # Insere o novo subtópico
                sections.append({'section_'+linha[3]: {'numero:':linha[3], 'titulo':linha[4], 'pagina':linha[0], 'linha': linha[1]}})
                textos   = []
                item_atu.append(linha[3])
            else:
                # Trata uma linha ordinária. 
                textos.append(linha[4]+'\n')
        
        # trata o encerramento 
        # carrega o texto da seção corrente
        sections[nivel]['section_' + item].update({'texto':self.conteudo(textos)})
        while nivnew <= nivel:
            if nivel==0:
                cap_dict['capitulo_' + cap_atu].update(sections[nivel])
                break
            else:
                sections[nivel-1]['section_'+ item_atu[len(item_atu)-2]].update(sections[nivel])
                
            del sections[nivel]
            nivel -= 1
            del item_atu[len(item_atu)-1]
            textos = []
        
        livro.update(cap_dict)
        return livro


    #
    # Salva o arquivo json para carga na base de conhecimento
    #
    def salva_json(self, livro, path_out, nome):
        # Salva a estrutura Json gerada
        if nome !="":
            self.linhas.book.titulo = nome + ('.json' if nome[-4:-1]!='.json' else '')
        else:
            self.linhas.book.titulo += ".json"
            
        with open(path_out+self.linhas.book.titulo, "w", encoding="utf-8") as f:
            json.dump(livro, f, ensure_ascii=False, indent=5)   
        
        print('Livro gerado no formato json', path_out+self.linhas.book.titulo)

    