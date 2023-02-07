# Análise Sintática Ascendente

Implementação desenvolvida para a disciplina de Compiladores, no Bacharelado em Ciência da Computação pela Universidade Federal de Lavras (UFLA).

Semestre: 2022/2

Professor: Maurício Souza

Alunos:

- <a href="https://github.com/GregoSX">Guilherme Grego</a>

- <a href="https://github.com/Victorgonl">Victor Gonçalves Lima</a>

# Descrição

A seguinte implementação, escrita em Python, recebe de entrada uma gramática de $n$ regras e gera:

- Os conjuntos de itens LR(0) e LR(1)

- Tabela LR(0), SLR(1) e CLR(1)

- A classificação da gramática em LR(0), SLR(1) e CLR(1)

# Funcionamento

Dada um número booleano, símbolizando se deve ou não gerar termos LR(1) (look-ahead), o número de regras da gramática $n$, e as $n$ regras linha por linha no formato $S$ -> $aSb$

    0
    2
    S -> aSb
    S -> ab

O algoritmo implementado irá criar um objeto do tipo ```Gramática```, que armazenará suas regras em um dicionário

    {'S': ['aSb', 'ab']}

Em seguida, a partir da **gramática**, irá criar um objeto do tipo ```Autômato```, que por sua vez irá criar objetos do tipo ```Estado```. O autômato irá aplicar algorítmos de **fechamento**, **seguidores**, **primeiros** e suas variações caso for trabalhar com **look-ahead**. Os algoritmos implementados trabalham com a estrutura de dados de conjunto, seja de símbolos ou regras, aplicando as devidas recursões.

    Estados:
    Estado 0: {("S'", '.S'), ('S', '.ab'), ('S', '.aSb')}
    Transições de 0: ('a', 2) ('S', 1)
    Estado 1: {("S'", 'S.')}
    Transições de 1:
    Estado 2: {('S', '.ab'), ('S', 'a.b'), ('S', 'a.Sb'), ('S', '.aSb')}
    Transições de 2: ('a', 2) ('S', 4) ('b', 3)
    Estado 3: {('S', 'ab.')}
    Transições de 3:
    Estado 4: {('S', 'aS.b')}
    Transições de 4: ('b', 5)
    Estado 5: {('S', 'aSb.')}
    Transições de 5:

A partir da **gramática** e do **autômato**, será criado um objeto do tipo ```Tabela```, que será responsável por implementar os algoritmos de **SHIFT**, **REDUCE**, **ACCEPT** E **GOTO** e testar se a tabela pode ser montada sem conflitos pelos algoritmos de **REDUCE** de LR(0), SLR(1) e CLR(!), definindo o tipo da gramática. A partir de uma biblioteca externa, *tabulate*, é gerado uma tabela formatada.

    Tabela:
    (0): S -> aSb
    (1): S -> ab

    ACTION | GOTO
    +----+-----+-----+-----+-----+
    |    |  $  |  a  |  b  |  S  |
    +====+=====+=====+=====+=====+
    |  0 |     | S2  |     |  1  |
    +----+-----+-----+-----+-----+
    |  1 | ACC |     |     |     |
    +----+-----+-----+-----+-----+
    |  2 |     | S2  | S5  |  3  |
    +----+-----+-----+-----+-----+
    |  3 |     |     | S4  |     |
    +----+-----+-----+-----+-----+
    |  4 | R0  | R0  | R0  |     |
    +----+-----+-----+-----+-----+
    |  5 | R1  | R1  | R1  |     |
    +----+-----+-----+-----+-----+

    Tipo de gramática: LR(0)

# Exemplos

**Observação:** como os algoritmos utilizam conjuntos, e não há ordem dos elementos nos mesmos, a execução do código determina a ordem em que os elementos serão chamados, gerando saídas em ordens diferentes para diferentes execuções, mas que expressam a mesma ideia e coerência com a entrada.

## LR(0)

### Entrada

    0
    2
    S -> aSb
    S -> ab

### Saída

    Gramática:
    {'S': ['aSb', 'ab']}

    Estados:
    Estado 0: {('S', '.aSb'), ("S'", '.S'), ('S', '.ab')}
    Transições de 0: ('S', 5) ('a', 1)
    Estado 1: {('S', '.aSb'), ('S', 'a.b'), ('S', '.ab'), ('S', 'a.Sb')}
    Transições de 1: ('a', 1) ('S', 3) ('b', 2)
    Estado 2: {('S', 'ab.')}
    Transições de 2:
    Estado 3: {('S', 'aS.b')}
    Transições de 3: ('b', 4)
    Estado 4: {('S', 'aSb.')}
    Transições de 4:
    Estado 5: {("S'", 'S.')}
    Transições de 5:

    Tabela:
    (0): S -> aSb
    (1): S -> ab

    ACTION | GOTO
    +----+-----+-----+-----+-----+
    |    |  $  |  a  |  b  |  S  |
    +====+=====+=====+=====+=====+
    |  0 |     | S1  |     |  5  |
    +----+-----+-----+-----+-----+
    |  1 |     | S1  | S2  |  3  |
    +----+-----+-----+-----+-----+
    |  2 | R1  | R1  | R1  |     |
    +----+-----+-----+-----+-----+
    |  3 |     |     | S4  |     |
    +----+-----+-----+-----+-----+
    |  4 | R0  | R0  | R0  |     |
    +----+-----+-----+-----+-----+
    |  5 | ACC |     |     |     |
    +----+-----+-----+-----+-----+

    Tipo de gramática: LR(0)

## SLR(1)

### Entrada

    0
    3
    E -> T+E
    E -> T
    T -> n

### Saída

    Gramática:
    {'E': ['T+E', 'T'], 'T': ['n']}

    Estados:
    Estado 0: {('E', '.T+E'), ('T', '.n'), ("E'", '.E'), ('E', '.T')}
    Transições de 0: ('T', 2) ('E', 5) ('n', 1)
    Estado 1: {('T', 'n.')}
    Transições de 1:
    Estado 2: {('E', 'T.'), ('E', 'T.+E')}
    Transições de 2: ('+', 3)
    Estado 3: {('E', '.T+E'), ('T', '.n'), ('E', 'T+.E'), ('E', '.T')}
    Transições de 3: ('T', 2) ('E', 4) ('n', 1)
    Estado 4: {('E', 'T+E.')}
    Transições de 4:
    Estado 5: {("E'", 'E.')}
    Transições de 5:

    Tabela:
    (0): T -> n
    (1): E -> T+E
    (2): E -> T

    ACTION | GOTO
    +----+-----+-----+-----+-----+-----+
    |    |  $  |  +  |  n  |  E  |  T  |
    +====+=====+=====+=====+=====+=====+
    |  0 |     |     | S1  |  5  |  2  |
    +----+-----+-----+-----+-----+-----+
    |  1 | R0  | R0  |     |     |     |
    +----+-----+-----+-----+-----+-----+
    |  2 | R2  | S3  |     |     |     |
    +----+-----+-----+-----+-----+-----+
    |  3 |     |     | S1  |  4  |  2  |
    +----+-----+-----+-----+-----+-----+
    |  4 | R1  |     |     |     |     |
    +----+-----+-----+-----+-----+-----+
    |  5 | ACC |     |     |     |     |
    +----+-----+-----+-----+-----+-----+

    Tipo de gramática: SLR(1)

## CLR(1)

### Entrada

    1
    3
    S -> AA
    A -> aA
    A -> b

### Saída

    Gramática:
    {'S': ['AA'], 'A': ['aA', 'b']}

    Estados:
    Estado 0: {('A', '.b', 'ab'), ('A', '.aA', 'ab'), ('S', '.AA', '$'), ("S'", '.S', '$')}
    Transições de 0: ('A', 2) ('a', 8) ('b', 1) ('S', 7)
    Estado 1: {('A', 'b.', 'ab')}
    Transições de 1:
    Estado 2: {('A', '.aA', '$'), ('A', '.b', '$'), ('S', 'A.A', '$')}
    Transições de 2: ('b', 5) ('a', 3) ('A', 6)
    Estado 3: {('A', '.aA', '$'), ('A', '.b', '$'), ('A', 'a.A', '$')}
    Transições de 3: ('b', 5) ('A', 4) ('a', 3)
    Estado 4: {('A', 'aA.', '$')}
    Transições de 4:
    Estado 5: {('A', 'b.', '$')}
    Transições de 5:
    Estado 6: {('S', 'AA.', '$')}
    Transições de 6:
    Estado 7: {("S'", 'S.', '$')}
    Transições de 7:
    Estado 8: {('A', '.b', 'ab'), ('A', '.aA', 'ab'), ('A', 'a.A', 'ab')}
    Transições de 8: ('A', 9) ('b', 1) ('a', 8)
    Estado 9: {('A', 'aA.', 'ab')}
    Transições de 9:

    Tabela:
    (0): A -> aA
    (1): A -> b
    (2): S -> AA

    ACTION | GOTO
    +----+-----+-----+-----+-----+-----+
    |    |  $  |  a  |  b  |  A  |  S  |
    +====+=====+=====+=====+=====+=====+
    |  0 |     | S8  | S1  |  2  |  7  |
    +----+-----+-----+-----+-----+-----+
    |  1 |     | R1  | R1  |     |     |
    +----+-----+-----+-----+-----+-----+
    |  2 |     | S3  | S5  |  6  |     |
    +----+-----+-----+-----+-----+-----+
    |  3 |     | S3  | S5  |  4  |     |
    +----+-----+-----+-----+-----+-----+
    |  4 | R0  |     |     |     |     |
    +----+-----+-----+-----+-----+-----+
    |  5 | R1  |     |     |     |     |
    +----+-----+-----+-----+-----+-----+
    |  6 | R2  |     |     |     |     |
    +----+-----+-----+-----+-----+-----+
    |  7 | ACC |     |     |     |     |
    +----+-----+-----+-----+-----+-----+
    |  8 |     | S8  | S1  |  9  |     |
    +----+-----+-----+-----+-----+-----+
    |  9 |     | R0  | R0  |     |     |
    +----+-----+-----+-----+-----+-----+

    Tipo de gramática: CLR(1)