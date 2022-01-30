#include <stdlib.h>
#include <stdio.h>

static void print_flag() {
    int flag[] = {70, 76, 65, 71, 123, 97, 115, 115, 101, 109, 98, 108, 101, 117, 114, 125};
    for (int i = 0; i < 16; i++) {
        printf("%c", flag[i]);
    }
}


int est_mot_de_passe_correct(const char *mdp) {
    int sum = 0;
    while (*mdp) {
        sum += *mdp;
        mdp++;
    }
    return sum == 512;
}

int main(void) {
    //"bbbbx"
    while (1) {
        printf("Entrez le mot de passe :\n> ");
        char input[32] = {0};
        scanf("%30s", input);
        if (est_mot_de_passe_correct(input)) {
            printf("Mot de passe correct !\n");
            printf("Voici le flag : '");
            print_flag();
            printf("'\n");
            exit(1);
        } else {
            printf("Mauvais mot de passe\n");
        }
    }
}
