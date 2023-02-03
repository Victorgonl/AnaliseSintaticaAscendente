import copy
import tabulate

class Gramática:
    def __init__(self):
        self.símbolo_inicial = ""
        self.regras = {}
        self.terminais = set()
        self.variáveis = set()
        self.regras_identificadas = {}
        self.número_de_regras = 0
        return
    def imprimir(self):
        print("Gramática:")
        for i in range(self.número_de_regras):
            print("(", i, "): ", self.regras_identificadas[i][0], " -> ", self.regras_identificadas[i][1], sep="")
        return
    def inserir_regra(self, termo_gerador, termo_gerado):
        if self.símbolo_inicial == "":
            self.símbolo_inicial = termo_gerador
        if not termo_gerador in self.regras.keys():
            self.regras[termo_gerador] = []
        self.regras[termo_gerador].append(termo_gerado)
        for i in termo_gerado:
            if i.islower():
                self.terminais.add(i)
        self.variáveis.add(termo_gerador)
        self.regras_identificadas[self.número_de_regras] = (termo_gerador, termo_gerado)
        self.número_de_regras += 1
        return
    def estender_gramática(self):
        novo_símbolo_inicial = self.símbolo_inicial + "'"
        self.inserir_regra(novo_símbolo_inicial, self.símbolo_inicial)
        self.símbolo_inicial = novo_símbolo_inicial
        return
    def fechamento(self):
        novas_regras = {}
        for termo_gerador in self.regras.keys():
            for termo_gerado in self.regras[termo_gerador]:
                if not termo_gerador in novas_regras.keys():
                    novas_regras[termo_gerador] = []
                novas_regras[termo_gerador].append("." + termo_gerado)
        self.regras = novas_regras

def símbolo_após_ponto(termo):
        if termo[-1] != ".":
            for i in range(len(termo)):
                if termo[i] == ".":
                    return termo[i + 1]
        else:
            return ""

class Estado:
    def __init__(self, gramática):
        self.regras = {}
        self.símbolos_a_serem_lidos = set()
        for termo_gerador in gramática.regras.keys():
            for termo_gerado in gramática.regras[termo_gerador]:
                self.inserir_regra(termo_gerador, termo_gerado)
    def inserir_regra(self, termo_gerador, termo_gerado):
        if not termo_gerador in self.regras.keys():
            self.regras[termo_gerador] = []
        self.regras[termo_gerador].append(termo_gerado)
        for termo_gerador in self.regras.keys():
            for termo_gerado in self.regras[termo_gerador]:
                símbolo = símbolo_após_ponto(termo_gerado)
                if símbolo != "":
                    self.símbolos_a_serem_lidos.add(símbolo)
        return

class Autômato:
    def __init__(self, gramática):
        gramática = copy.deepcopy(gramática)
        self.estados = []
        self.transições = []
        self.index_do_estado_inicial = 0
        gramática.estender_gramática()
        gramática.fechamento()
        self.criar_estado_inicial(gramática)
        self.criar_estados_recursivamente(self.estados[self.index_do_estado_inicial], self.index_do_estado_inicial)
        return
    def criar_estado_inicial(self, gramática):
        estado_inicial = Estado(gramática)
        self.estados.append(estado_inicial)
        empty_set = set()
        self.transições.append(empty_set)
        return
    def criar_estados_recursivamente(self, estado, index_do_estado):
        index_do_novo_estado = index_do_estado
        for símbolo_lido in estado.símbolos_a_serem_lidos:
            nova_gramática = Gramática()
            for termo_gerador in estado.regras.keys():
                for termo_gerado in estado.regras[termo_gerador]:
                    if símbolo_após_ponto(termo_gerado) == símbolo_lido:
                        novo_termo_gerado = termo_gerado.replace("." + símbolo_lido, símbolo_lido + ".")
                        nova_gramática.inserir_regra(termo_gerador, novo_termo_gerado)
            novo_estado = Estado(nova_gramática)
            index_do_novo_estado = len(self.estados)
            self.estados.append(novo_estado)
            empty_set = set()
            self.transições.append(empty_set)
            self.transições[index_do_estado].add((símbolo_lido, index_do_novo_estado))
            self.criar_estados_recursivamente(novo_estado, index_do_novo_estado)
        for termo_gerador in self.estados[index_do_novo_estado].regras.keys():
            for termo_gerado in self.estados[index_do_novo_estado].regras[termo_gerador]:
                símbolo = símbolo_após_ponto(termo_gerado)
                if símbolo in self.estados[self.index_do_estado_inicial].regras.keys():
                    for termo in estado.regras[símbolo]:
                        self.estados[index_do_novo_estado].inserir_regra(símbolo, termo)
                        self.transições[index_do_novo_estado].add((símbolo_após_ponto(termo), index_do_novo_estado))
        return
    def imprimir(self):
        for i in range(len(self.estados)):
            print("Estado ", i, ": ", sep="", end="")
            print(self.estados[i].regras)
            print("Transições de ", i, ": ", sep="", end="")
            for transição in self.transições[i]:
                print(transição, end=" ")
            print()
        return

class Tabela:
    def __init__(self, gramática, autômato):
        gramática = copy.deepcopy(gramática)
        self.número_de_estados = len(autômato.estados)
        self.terminais = gramática.terminais.union(set("$"))
        self.variáveis = gramática.variáveis
        self.ACTION = {terminal: ["  " for _ in range(len(autômato.estados))] for terminal in self.terminais}
        self.GOTO = {variável: ["   " for _ in range(len(autômato.estados))] for variável in self.variáveis}
        # operações SHIFT
        for terminal in self.terminais:
            for i in range(len(autômato.estados)):
                for j in range(len(autômato.estados)):
                    if (terminal, j) in autômato.transições[i]:
                        self.ACTION[terminal][i] = " S" + str(j)
        # operações GOTO
        for variável in self.variáveis:
            for i in range(len(autômato.estados)):
                for j in range(len(autômato.estados)):
                    if (variável, j) in autômato.transições[i]:
                        self.GOTO[variável][i] = " " + str(j) + " "
        # operações REDUCE e ACCEPT
        for i in range(len(autômato.estados)):
            for termo_gerador in autômato.estados[i].regras.keys():
                for termo_gerado in autômato.estados[i].regras[termo_gerador]:
                    if termo_gerado[-1] == ".":
                        if termo_gerador == termo_gerado[0] + "'":
                            self.ACTION["$"][i] = "ACC"
                            break
                        else:
                            for terminal in self.terminais:
                                for j in range(len(gramática.regras_identificadas)):
                                    if gramática.regras_identificadas[j][0] == termo_gerador:
                                        if gramática.regras_identificadas[j][1] == termo_gerado[:-1]:
                                            self.ACTION[terminal][i] = "R" + str(j)
        return
    def imprimir(self):
        # cria o cabeçalho
        terminais = []
        variáveis = []
        for terminal in self.terminais:
            terminais.append(terminal)
        terminais.sort()
        for variável in self.variáveis:
            variáveis.append(variável)
        variáveis.sort()
        cabeçalho = terminais + variáveis
        # cria a matriz da tabela
        matriz = [["" for _ in range(len(cabeçalho) + 1)] for _ in range(self.número_de_estados)]
        # coloca identificações dos estados
        for i in range(self.número_de_estados):
            matriz[i][0] = str(i)
        # atribui valores as células
        valores = self.ACTION
        valores.update(self.GOTO)
        for i in range(self.número_de_estados):
            for j in range(len(cabeçalho)):
                matriz[i][j + 1] = valores[cabeçalho[j]][i]
        # cria e imprime a matriz com a biblioteca 'tabulate'
        tabela = tabulate.tabulate(matriz, headers=cabeçalho, tablefmt="grid")
        print("ACTION | GOTO")
        print(tabela)
        return


def main():
    gramática = Gramática()
    # lê regras das gramáticas
    número_de_regras = int(input("Digite o número de regras (linhas) a ser lido: "))
    print("Digite as regras da gramática no formato 'S -> aSb', linha por linha:")
    for i in range(número_de_regras):
        regra = input(str(i) + ": ").replace(" ", "").split("->")
        gramática.inserir_regra(regra[0], regra[1])
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