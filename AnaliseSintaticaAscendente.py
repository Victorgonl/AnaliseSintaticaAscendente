import copy # para cópia de objetos e seus valores
import tabulate # biblioteca externa para geração de tabelas


# constantes

EPSILON = "ε"
EOF = "$"
NULO = ""
SÍMBOLO_DE_ESTENDIDO = "'"


# funções para gramática

# retorna o śimbolo após ponto de uma projeção
def símbolo_após_ponto(projeção):
    for i in range(len(projeção)):
        if (projeção[i] == ".") and (i + 1 < len(projeção)):
            return projeção[i + 1]
    return NULO

# retorna o conjunto fechamento de uma projeção da gramática
def fechamento(gramática, não_terminal, projeção):
    conjunto_fechamento = set()
    conjunto_fechamento.add((não_terminal, projeção))
    símbolo = símbolo_após_ponto(projeção)
    if símbolo in gramática.não_terminais():
        for p in gramática.regras[símbolo]:
            nova_projeção = "." + p
            conjunto_fechamento.add((símbolo, nova_projeção))
            conjunto = fechamento(gramática, símbolo, nova_projeção)
            conjunto_fechamento = conjunto_fechamento.union(conjunto)
    return conjunto_fechamento

# retorna o conjunto primeiros de um símbolo da gramática
def primeiros(gramática, símbolo):
    conjunto_primeiros = set()
    if símbolo in gramática.terminais():
        conjunto_primeiros.add(símbolo)
        return conjunto_primeiros
    if EPSILON in gramática.regras[símbolo]:
        conjunto_primeiros.add(EPSILON)
    for regra in gramática.regras[símbolo]:
        if regra[0] in gramática.não_terminais():
            for i in range(len(regra) - 1):
                if EPSILON in primeiros(gramática, regra[i]):
                    conjunto = conjunto_primeiros.union(primeiros(gramática, regra[i]))
                    conjunto.discard(EPSILON)
                    conjunto = conjunto.union(primeiros(gramática, regra[i + 1]))
                    conjunto.discard(EPSILON)
                    conjunto_primeiros = conjunto_primeiros.union(conjunto)
                    if i + 1 == len(regra) - 1:
                        if EPSILON in primeiros(gramática, regra[i + 1]):
                            conjunto_primeiros.add(EPSILON)
                else:
                    conjunto_primeiros = conjunto_primeiros.union(primeiros(gramática, regra[i]))
                    break
        elif regra[0] in gramática.terminais() and regra[0] != EPSILON:
            conjunto_primeiros.add(regra[0])
    return conjunto_primeiros

# retorna o conjunto seguidores de um símbolo da gramática
def seguidores(gramática, símbolo):
    conjunto_seguidores = set()
    if símbolo == gramática.símbolo_inicial:
        conjunto_seguidores.add(EOF)
    for variável in gramática.regras.keys():
        for regra in gramática.regras[variável]:
            for i in range(0, len(regra)):
                if i < len(regra) - 1:
                    if regra[i] == símbolo:
                        conjunto = primeiros(gramática, regra[i + 1])
                        conjunto.discard(EPSILON)
                        conjunto_seguidores = conjunto_seguidores.union(conjunto)
                        if EPSILON in primeiros(gramática, regra[i + 1]):
                            conjunto = primeiros(gramática, regra[i + 1])
                            conjunto.discard(EPSILON)
                            conjunto = conjunto.union(seguidores(gramática, variável))
                            conjunto_seguidores = conjunto_seguidores.union(conjunto)
                else:
                    if regra[i] == símbolo and símbolo != variável:
                        conjunto_seguidores = conjunto_seguidores.union(seguidores(gramática, variável))
    return conjunto_seguidores


# classes

# representação de gramáticas
class Gramática:
    def __init__(self):
        self.regras = {}
        self.símbolo_inicial = NULO
    def adicionar_regra(self, não_terminal, projeção):
        if not não_terminal in self.não_terminais():
            if len(self.regras) == 0:
                self.símbolo_inicial = não_terminal
            self.regras[não_terminal] = []
        if projeção in self.regras[não_terminal]:
            return
        self.regras[não_terminal].append(projeção)
    def não_terminais(self):
        return set(self.regras.keys())
    def terminais(self):
        não_terminais = self.não_terminais()
        símbolos = set()
        for não_terminal in não_terminais:
            for projeção in self.regras[não_terminal]:
                for símbolo in projeção:
                    símbolos.add(símbolo)
        return símbolos.difference(não_terminais)
    def imprimir(self):
        print("Gramática:")
        print(self.regras)
        return

# representação de um estado de um autômato para Parser
class Estado:
    def __init__(self, identificação) -> None:
        self.identificação = identificação
        self.regras = set()
    def símbolos_a_serem_lidos(self):
        conjunto = set()
        for (não_terminal, projeção) in self.regras:
            símbolo = símbolo_após_ponto(projeção)
            if símbolo != NULO:
                conjunto.add(símbolo)
        return conjunto
    def imprimir(self):
        print(self.regras)

# representação de um autômato para Parser
class Autômato:
    def __init__(self, gramática):
        self.estados = []
        self.transições = []
        self.defininir_estado_inicial(gramática)
        self.denifir_estados_recursivamente(gramática, 0)
    def defininir_estado_inicial(self, gramática):
        estado_inicial = Estado(0)
        não_terminal = gramática.símbolo_inicial + SÍMBOLO_DE_ESTENDIDO
        projeção = "." + gramática.símbolo_inicial
        estado_inicial.regras = fechamento(gramática, não_terminal, projeção)
        self.estados.append(estado_inicial)
        empty_set = set()
        self.transições.append(empty_set)
    def denifir_estados_recursivamente(self, gramática, index_do_estado):
        for símbolo_de_transição in self.estados[index_do_estado].símbolos_a_serem_lidos():
            criar_novo_estado = True
            novas_regras = set()
            empty_set = set()
            self.transições.append(empty_set)
            for (variável, projeção) in self.estados[index_do_estado].regras:
                símbolo = símbolo_após_ponto(projeção)
                if símbolo == símbolo_de_transição:
                    novas_regras = novas_regras.union(fechamento(gramática, variável, projeção.replace("." + símbolo, símbolo + ".")))
            for i in range(len(self.estados)):
                if novas_regras == self.estados[i].regras:
                    self.transições[index_do_estado].add((símbolo_de_transição, i))
                    criar_novo_estado = False
            if criar_novo_estado:
                index_do_novo_estado = len(self.estados)
                novo_estado = Estado(index_do_novo_estado)
                novo_estado.regras = copy.deepcopy(novas_regras)
                self.transições[index_do_estado].add((símbolo_de_transição, index_do_novo_estado))
                self.estados.append(novo_estado)
                self.denifir_estados_recursivamente(gramática, index_do_novo_estado)
        return
    def imprimir(self):
        print("Estados:")
        for i in range(len(self.estados)):
            print("Estado ", i, ": ", sep="", end="")
            print(self.estados[i].regras)
            print("Transições de ", i, ": ", sep="", end="")
            for transição in self.transições[i]:
                print(transição, end=" ")
            print()
        return

# representação para a tabela do Parser
class Tabela():
    def __init__(self, gramática, autômato):
        self.tipo_de_gramática = NULO
        self.lista_de_regras = []
        for não_terminal in gramática.não_terminais():
            for projeção in gramática.regras[não_terminal]:
                self.lista_de_regras.append((não_terminal, projeção))
        self.ACTION = {}
        self.ACTION[EOF] = [NULO for _ in range(len(autômato.estados))]
        for terminal in gramática.terminais():
            self.ACTION[terminal] = [NULO for _ in range(len(autômato.estados))]
        self.GOTO = {}
        for não_terminal in gramática.não_terminais():
            self.GOTO[não_terminal] = [NULO for _ in range(len(autômato.estados))]
        self.operações_de_SHIFT(gramática, autômato)
        self.operações_de_GOTO(gramática, autômato)
        # se for possível realizar as operações sem conflito, é LR(0)
        if self.operações_de_REDUCE_e_ACCEPT_para_LR0(gramática, autômato):
            self.tipo_de_gramática = "LR(0)"
        # se não, se for possível realizar as operações sem conflito, é SLR(1)
        elif self.operações_de_REDUCE_e_ACCEPT_para_SLR1(gramática, autômato):
            self.tipo_de_gramática = "SLR(1)"
    def operações_de_SHIFT(self, gramática, autômato):
        for i in range(len(autômato.estados)):
            for terminal in gramática.terminais():
                for (símbolo_lido, estado_destino) in autômato.transições[i]:
                        if símbolo_lido == terminal:
                            self.ACTION[terminal][i] = "S" + str(estado_destino)
    def operações_de_GOTO(self, gramática, autômato):
        for i in range(len(autômato.estados)):
            for não_terminal in gramática.não_terminais():
                for (símbolo_lido, estado_destino) in autômato.transições[i]:
                        if símbolo_lido == não_terminal:
                            self.GOTO[não_terminal][i] = str(estado_destino)
    def operações_de_REDUCE_e_ACCEPT_para_LR0(self, gramática, autômato):
        ACTION = copy.deepcopy(self.ACTION)
        for i in range(len(autômato.estados)):
            for (não_terminal, projeção) in autômato.estados[i].regras:
                if símbolo_após_ponto(projeção) == NULO:
                    # operação de ACCEPT
                    if não_terminal == gramática.símbolo_inicial + SÍMBOLO_DE_ESTENDIDO:
                        ACTION[EOF][i] = "ACC"
                    # operações de REDUCE
                    else:
                        for identificação in range(len(self.lista_de_regras)):
                            (x, y) = self.lista_de_regras[identificação]
                            if y == projeção[:-1]:
                                for terminal in ACTION.keys():
                                    if ACTION[terminal][i] != NULO:
                                        return False
                                    ACTION[terminal][i] = "R" + str(identificação)
        self.ACTION = ACTION
        return True
    def operações_de_REDUCE_e_ACCEPT_para_SLR1(self, gramática, autômato):
        ACTION = copy.deepcopy(self.ACTION)
        for i in range(len(autômato.estados)):
            for (não_terminal, projeção) in autômato.estados[i].regras:
                if símbolo_após_ponto(projeção) == NULO:
                    # operação de ACCEPT
                    if não_terminal == gramática.símbolo_inicial + SÍMBOLO_DE_ESTENDIDO:
                        ACTION[EOF][i] = "ACC"
                    # operações de REDUCE
                    else:
                        for identificação in range(len(self.lista_de_regras)):
                            (x, y) = self.lista_de_regras[identificação]
                            if y == projeção[:-1]:
                                for terminal in seguidores(gramática, não_terminal):
                                    if ACTION[terminal][i] != NULO:
                                        return False
                                    ACTION[terminal][i] = "R" + str(identificação)
        self.ACTION = ACTION
        return True


    def imprimir(self):
        # grmática não reconhecida
        if self.tipo_de_gramática == NULO:
            print("Gramática não reconhecida!")
            return
        # cria o cabeçalho
        cabeçalho_ACTION = list(self.ACTION.keys())
        cabeçalho_ACTION.sort()
        cabeçalho_GOTO = list(self.GOTO.keys())
        cabeçalho_GOTO.sort()
        cabeçalho = cabeçalho_ACTION + cabeçalho_GOTO
        # cria a matriz da tabela
        número_de_estados = len(self.ACTION[cabeçalho_ACTION[0]])
        matriz = [[NULO for _ in range(len(cabeçalho) + 1)] for _ in range(número_de_estados)]
        # coloca identificações dos estados
        for i in range(número_de_estados):
            matriz[i][0] = str(i)
        # atribui valores as células
        valores = self.ACTION
        valores.update(self.GOTO)
        for i in range(número_de_estados):
            for j in range(len(cabeçalho)):
                matriz[i][j + 1] = valores[cabeçalho[j]][i]
        # cria e imprime a matriz com a biblioteca 'tabulate'
        tabela = tabulate.tabulate(matriz, headers=cabeçalho, tablefmt="grid", stralign='center')
        print("Tabela:")
        for i in range(len(self.lista_de_regras)):
            (não_terminal, projeção) = self.lista_de_regras[i]
            print("(", i, "): ", não_terminal, " -> ", projeção, sep="")
        print()
        print("ACTION | GOTO")
        print(tabela)
        print("Tipo de gramática:", self.tipo_de_gramática)
        return

def main():
    gramática = Gramática()
    # lê regras das gramáticas
    número_de_regras = int(input("Digite o número de regras (linhas) a ser lido: "))
    print("Digite as regras da gramática no formato 'S -> aSb', linha por linha:")
    for i in range(número_de_regras):
        regra = input(str(i) + ": ").replace(" ", "").split("->")
        gramática.adicionar_regra(regra[0], regra[1])
    print()
    gramática.imprimir()
    print()
    autômato = Autômato(gramática)
    autômato.imprimir()
    print()
    tabela = Tabela(gramática, autômato)
    tabela.imprimir()
    return

main()