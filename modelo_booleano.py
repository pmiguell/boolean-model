# Para o funcionamento correto do código, acrescente o caminho da pasta nos arquivos da base, por exemplo:
# base1 1/a.txt
# base1 1/b.txt
# base1 1/c.txt
# base_samba 1/a_flor_e_o_espinho.samba

# Exemplo de comando para testar o código: py waxm_corretor_modelo_booleano.pyc "base1 1/base.txt" "base1 1/consulta.txt" modelo_booleano.py

import spacy
import sys

nlp = spacy.load("pt_core_news_lg")

nome_arquivos = dict()

def gerarIndiceInvertido(texto, doc_id, indiceInvertido, nome_arquivo):
    doc = nlp(texto.lower())

    tokens = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_space and not token.is_punct and not ' ' in token.lemma_]

    for token in tokens:
        if token in indiceInvertido:
            if doc_id in indiceInvertido[token]:
                indiceInvertido[token][doc_id] += 1
            else:
                indiceInvertido[token][doc_id] = 1
        else:
            indiceInvertido[token] = {doc_id: 1}

    nome_arquivos[doc_id] = nome_arquivo

    return indiceInvertido

def processarDocumentos(caminhoBase, caminhoConsulta):
    indiceInvertido = dict()

    with open(caminhoBase, "r", encoding="utf-8") as base:
        for i, line in enumerate(base, start=1):
            caminhoArquivo = line.strip()
            with open(caminhoArquivo, "r", encoding="utf-8") as arquivo:
                conteudo = arquivo.read()
                gerarIndiceInvertido(conteudo, i, indiceInvertido, caminhoArquivo)
                arquivo.close()

    with open("indice.txt", "w", encoding="utf-8") as indiceGerado:
        for termo, documentos in indiceInvertido.items():
            lista_documentos = [f"{doc_id},{freq}" for doc_id, freq in documentos.items()]
            indiceGerado.write(f"{termo}: {' '.join(lista_documentos)}\n")

    with open(caminhoConsulta, "r", encoding="utf-8") as conteudo:
        consulta = conteudo.read()

    documentos_resultado = modeloBooleano(consulta, indiceInvertido)

    with open("resposta.txt", "w", encoding="utf-8") as resposta:
        resposta.write(str(len(documentos_resultado)) + '\n')
        for documento in documentos_resultado:
            resposta.write(documento + '\n')

def modeloBooleano(consulta, indiceInvertido):
    doc2 = nlp(consulta.lower())

    operadores = []
    operandos = []

    elementos = [token.lemma_ for token in doc2 if not token.is_stop and not token.is_space]

    def aplicar_operador():
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
            resultado = operando1 + [doc_id for doc_id in operando2 if doc_id not in operando1]
            operandos.append(resultado)

    precedencia = {'!': 3, '&': 2, '|': 1}

    for elemento in elementos:
        if elemento not in {'&', '|', '!'}:
            if elemento in indiceInvertido:
                doc_list = list(indiceInvertido[elemento].keys())
                operandos.append(doc_list)
            else:
                operandos.append([])
        else:
            while operadores and precedencia[operadores[-1]] >= precedencia[elemento]:
                aplicar_operador()
            operadores.append(elemento)

    while operadores:
        aplicar_operador()

    resultados = operandos.pop() if operandos else []
    nomes_arquivos_resultantes = [nome_arquivos[doc_id] for doc_id in sorted(resultados)]

    return sorted(nomes_arquivos_resultantes)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(1)

    caminhoBase = sys.argv[1]
    caminhoConsulta = sys.argv[2]
    processarDocumentos(caminhoBase, caminhoConsulta)
