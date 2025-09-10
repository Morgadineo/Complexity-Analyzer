# Analisador de Complexidades C (DESATUALIZADO)

Esta ferramenta foi desenvolvida para um projeto de pesquisa envolvendo análise
de complexidade de código C. Com a falta de ferramentas pequenas, open-sources
para a pesquisa, resolvi desenvolver a minha própria ferramenta utilizando a
linguagem Python.

O Analisador de Complexidades C atualmente trabalha com as seguintes
complexidades:
* [X] Quantidade de linhas:
    * Contagem de linhas totais;
    * Contagem de linhas efetivas.
* [X] Complexidade Ciclomática:
    * do programa todo;
    * de cada subprograma;
* [X] Métricas de Halstead:
    * Quantidade de operadores (n1);
    * Quantidade de operandos (n2);
    * Quantidade de operadores distintos (N1);
    * Quantidade de operandos distintos (N2);
    * Vocabulário do programa (n);
    * Tamanho do programa (N);
    * Tamanho estimado do programa (^N);
    * Volume do programa (V);
    * Dificuldade do programa (D);
    * Nível do programa (L);
    * Inteligência do programa (I);
    * Custo do programa (E);
    * Tempo requerido para programar (T);
    * Quantidade de Erros estimada.
* [X] Complexidade Cognitiva:
    * do programa todo;
    * de cada subprograma; 

## Significado de cada métrica:

(...)

## Como é feito a análise?

Para fazer a análise e quebra do código C, utilizei a biblioteca pycparse, que
realiza a quebra do arquivo fonte C pré-compilado em uma Árvore de Sintaxe
Abstrata (AST) e realiza a análise dos nós. A AST é representada através de uma
classe própria que possui métodos chamados quando um determinado nó é
encontrado. Com esses métodos, é possível obter as informações necessárias de cada estrutura
do código.

Com exceção das métricas de linhas, todas as outras são obtidas utilizando a
árvore de sintaxe abstrata. Para as métricas de linhas, foi necessária a análise
direta do código fonte c.

# Código C pré-compilado.

Utilizar o código C pré-compilado é uma das formas de passar o código para a
biblioteca do pycparser. Existe uma outra forma também, onde a própria biblioteca cuida do
processo de pré-compilação, porém, esse processo é um pouco mais díficil de
configurar.

A pré-compilação é a primeira grande etapa do processo de compilação do código,
onde o compilador realiza a análise sintática, léxica e lida também com as
diretivas de pré-compilação presentes no código C. O pycparser possui alguns
problemas em lidar com os comentários presentes no arquivo pré-compilado, por
isso é necessário a remoção dos comentários presentes no arquivo.

Para facilitar este processo, já configurei um Makefile para realizar a
pré-compilação de todos os códigos presentes no diretório "Examples/". Este
diretório pode ser configurado diretamente no Makefile.

Importante ressaltar que a ferramenta é capaz de fazer a análise de códigos
incompletos ou incorretos que normalmente seriam barradas em estágios
posteriores do processo de compilação.

## Fake-Headers do pycparser.

Outro detalhe fundamental da biblioteca pycparser é a utilização de fake-headers
no processo de pré-compilação. Como dito anteriormente, o analisador precisa
apenas do arquivo pré-compilado, porém, alguns detalhes são importantes para que
o gcc (compilador utilizado) consiga fazer a pré-compilação, como as bilbiotecas
utilizadas. Para o pycparser, só é importante saber que as bibliotecas presentes
no código EXISTEM, por isso passamos para o gcc (ou cpp->"C Pre Processor") um
pasta com as fake-headers do pycparser.

O arquivo 'Fake Header.txt' possui mais informações e detalhes sobre as
fake-headers do pycparser.

(...)

## OUTPUTS (desatualizado)
### Complexity
![output](https://github.com/user-attachments/assets/f68678e9-2f5c-4acd-8f92-5f0c6e416165)
### Functions Cyclomatic Complexity
![functions_output](https://github.com/user-attachments/assets/6a8be9ab-16e3-45ad-8497-28abdb532e18)
### Operators info
![operators_output](https://github.com/user-attachments/assets/a0b77172-9786-4193-a24e-780d165e1714)
### Operands info
![operands_output1](https://github.com/user-attachments/assets/68f41c55-21c4-440a-95d1-0199eefa3faa)
