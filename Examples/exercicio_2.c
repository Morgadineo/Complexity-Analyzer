/* tabuada.c
 * 
 * Por: Abrantes Araújo Silva Filho
 *      abrantesasf@computacaoraiz.com.br | abrantesasf@pm.me
 *
 *   EXERCÍCIO: "tabuada_restrita"
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
    
    // Pergunta para o usuário o número de início da tabuada:
    int inicio = get_int("Você quer começar a tabuada em qual número? ");
    
    // Pergunta para o usuário o número de fim da tabuada:
    int fim = get_int("Você quer terminar a tabuada em qual número? ");
    
    // Imprime a tabuada se inicio/fim fizerem sentido, ou uma mensagem de erro:
    if (inicio <= fim)
    {
        for (int i = inicio; i <= fim; i++)
        {
            printf("%d x %d = %d\n", n, i, n * i);
        }
    }
    else
    {
        printf("%s\n", "Erro na especificação da tabuada.");
    }
        
    // Sair do programa:
    return 0;
}


