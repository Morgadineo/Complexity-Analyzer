/* tabuada.c
 * 
 * Por: Abrantes Araújo Silva Filho
 *      abrantesasf@computacaoraiz.com.br | abrantesasf@pm.me
 *
 *   EXERCÍCIO: "tabuada"
 *   LINGUAGEM: C
 * OBSERVAÇÕES: permite o uso da cs50.h para facilitar a entrada de dados por
 *              alunos iniciantes
 */
#include <cs50.h>
#include <stdio.h>


/**
 * Função main do programa
 */
int main(void)
{
    // Pergunta para o usuário qual a tabuada que ele quer:
    int n = get_int("Você quer a tabuada de qual número? ");
    
    // Imprime a tabuada de 0 a 10:
    for (int i = 0; i <= 10; i++)
    {
        printf("%d x %d = %d\n", n, i, n * i);
    }
    
    // Sair do programa:
    return 0;
}


