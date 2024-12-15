/**
 * cash.c
 * 
 * Por: Abrantes Araújo Silva Filho
 *      abrantesasf@computacaoraiz.com.br | abrantesasf@pm.me
 *
 *        PSET: "cash"
 *   LINGUAGEM: C
 * OBSERVAÇÕES: permite o uso da cs50.h para facilitar a entrada de dados por
 *              alunos iniciantes
 */
#include <cs50.h>
#include <stdio.h>


/**
 * Protótipos das funções
 */
int get_troco(void);
int calcular_moedas50(int troco);
int calcular_moedas25(int troco);
int calcular_moedas10(int troco);
int calcular_moedas05(int troco);
int calcular_moedas01(int troco);


/**
 * Função MAIN
 */
int main(void)
{
    // Pergunta para o usuário qual o valor total do troco, em centavos:
    int troco = get_troco();

    // Calcula o número de moedas de 50 centavos a serem dadas ao cliente:
    int moedas50 = calcular_moedas50(troco);
    troco = troco - moedas50 * 50;
    
    // Calcula o número de moedas de 25 centavos a serem dadas ao cliente:
    int moedas25 = calcular_moedas25(troco);
    troco = troco - moedas25 * 25;

    // Calcula o número de moedas de 10 centavos a serem dadas ao cliente:
    int moedas10 = calcular_moedas10(troco);
    troco = troco - moedas10 * 10;

    // Calcula o número de moedas de 5 centavos a serem dadas ao cliente:
    int moedas05 = calcular_moedas05(troco);
    troco = troco - moedas05 * 5;

    // Calcula o número de moedas de 1 centavo a serem dadas ao cliente:
    int moedas01 = calcular_moedas01(troco);
    troco = troco - moedas01;

    // Quantidade total otimizada de moedas:
    int moedas = moedas50 + moedas25 + moedas10 + moedas05 + moedas01;

    // Imprime a quantidade total de moedas:
    printf("%i\n", moedas);
    
    // Termina o programa:
    return 0;
}


/**
 * Implementação das funções
 */
int get_troco(void)
{
    int temp;
    do
    {
        temp = get_int("Informe o troco devido (em centavos): ");
    }
    while (temp < 0);
    
    return temp;
}


int calcular_moedas50(int troco)
{
    return troco / 50;
}


int calcular_moedas25(int troco)
{
    return troco / 25;
}


int calcular_moedas10(int troco)
{
    return troco / 10;
}


int calcular_moedas05(int troco)
{
    return troco / 5;
}


int calcular_moedas01(int troco)
{
    return troco;
}


