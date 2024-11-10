import spacy

# Carrega o modelo de linguagem em português para processamento de texto com spaCy
nlp = spacy.load("pt_core_news_lg")

# Dicionário para mapear os IDs dos documentos aos seus respectivos nomes de arquivo
nome_arquivos = {}

def processar_texto(texto):
    """Processa o texto e extrai tokens relevantes (sem stopwords, espaços ou pontuação)."""
    doc = nlp(texto.lower())
    tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_space and not token.is_punct]
    return tokens

def atualizar_indice_invertido(tokens, doc_id, indice_invertido):
    """Atualiza o índice invertido com a frequência dos tokens."""
    for token in tokens:
        if token in indice_invertido:
            indice_invertido[token][doc_id] = indice_invertido[token].get(doc_id, 0) + 1
        else:
            indice_invertido[token] = {doc_id: 1}

def gerar_indice_invertido(texto, doc_id, indice_invertido, nome_arquivo):
    """Gera o índice invertido a partir do texto de um documento."""
    tokens = processar_texto(texto)
    atualizar_indice_invertido(tokens, doc_id, indice_invertido)
    nome_arquivos[doc_id] = nome_arquivo
    return indice_invertido

def construir_indice_invertido(caminho_base):
    """Constrói o índice invertido a partir dos documentos fornecidos."""
    indice_invertido = {}
    with open(caminho_base, "r", encoding="utf-8") as base:
        for i, caminho_arquivo in enumerate(base, start=1):
            caminho_arquivo = caminho_arquivo.strip()
            with open(caminho_arquivo, "r", encoding="utf-8") as arquivo:
                conteudo = arquivo.read()
                gerar_indice_invertido(conteudo, i, indice_invertido, caminho_arquivo)
    return indice_invertido

def salvar_indice(indice_invertido, caminho_saida):
    """Grava o índice invertido em um arquivo de saída."""
    with open(caminho_saida, "w", encoding="utf-8") as indice_gerado:
        for termo, documentos in indice_invertido.items():
            lista_documentos = [f"{doc_id},{freq}" for doc_id, freq in documentos.items()]
            indice_gerado.write(f"{termo}: {' '.join(lista_documentos)}\n")

def aplicar_operador(operadores, operandos):
    """Aplica um operador lógico entre os operandos."""
    operador = operadores.pop()
    if operador == '!':
        operando = operandos.pop()
        resultado = [doc_id for doc_id in nome_arquivos.keys() if doc_id not in operando]
        operandos.append(resultado)
    elif operador == '&':
        operando2 = operandos.pop()
        operando1 = operandos.pop()
        resultado = [doc_id for doc_id in operando1 if doc_id in operando2]
        operandos.append(resultado)
    elif operador == '|':
        operando2 = operandos.pop()
        operando1 = operandos.pop()
        resultado = list(set(operando1) | set(operando2))
        operandos.append(resultado)

def modelo_booleano(consulta, indice_invertido):
    """Executa a consulta usando o modelo booleano."""
    doc = nlp(consulta.lower())
    operadores = []
    operandos = []
    elementos = [token.lemma_ for token in doc if not token.is_stop and not token.is_space]

    precedencia = {'!': 3, '&': 2, '|': 1}

    for elemento in elementos:
        if elemento not in {'&', '|', '!'}:
            operandos.append(list(indice_invertido.get(elemento, {}).keys()))
        else:
            while operadores and precedencia[operadores[-1]] >= precedencia[elemento]:
                aplicar_operador(operadores, operandos)
            operadores.append(elemento)

    while operadores:
        aplicar_operador(operadores, operandos)

    resultados = operandos.pop() if operandos else []
    nomes_arquivos_resultantes = [nome_arquivos[doc_id] for doc_id in sorted(resultados)]
    return sorted(nomes_arquivos_resultantes)

def salvar_resultados(documentos_resultado, caminho_saida):
    """Grava os resultados da consulta em um arquivo de saída."""
    with open(caminho_saida, "w", encoding="utf-8") as resposta:
        resposta.write(str(len(documentos_resultado)) + '\n')
        for documento in documentos_resultado:
            resposta.write(documento + '\n')

def processar_documentos(caminho_base, caminho_consulta):
    """Processa os documentos e realiza a busca booleana."""
    indice_invertido = construir_indice_invertido(caminho_base)
    salvar_indice(indice_invertido, "indice.txt")

    with open(caminho_consulta, "r", encoding="utf-8") as arquivo_consulta:
        consulta = arquivo_consulta.read()

    documentos_resultado = modelo_booleano(consulta, indice_invertido)
    salvar_resultados(documentos_resultado, "resposta.txt")

if __name__ == "__main__":
    caminho_base = input("Digite o caminho da base de documentos: ")
    caminho_consulta = input("Digite o caminho da consulta: ")
    processar_documentos(caminho_base, caminho_consulta)
