#include <stdio.h>
#include <string.h>
#include <stdlib.h>

int main(void) {
    while (1) {
        printf("Entrez le mot de passe :\n> ");
        char input[32] = {0};
        scanf("%30s", input);
        if (strcmp(input, "FLAG{attention-aux-strings}") == 0) {
            printf("Mot de passe correct !\n");
            exit(1);
        } else {
            printf("Mauvais mot de passe\n");
        }
    }
}
