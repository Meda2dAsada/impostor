#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <sys/mman.h>
#include <semaphore.h>
#include <time.h>

#define PUERTO 5000
#define MAX_JUGADORES 5

const char *banco_palabras[] = {
    "Docker", "Sinaloa", "Ingenieria", "Python",
    "Gato", "Raytracer", "Gimnasio", "Blackjack"
};
const int num_palabras = sizeof(banco_palabras) / sizeof(banco_palabras[0]);

typedef struct {
    sem_t semaforo;
    int num_conectados;
    int num_listos;
    int palabras_listas;
    int votos_totales;
    char nombres[MAX_JUGADORES][50];
    char chat_palabras[MAX_JUGADORES][100];
    int votos[MAX_JUGADORES];
    int indice_impostor;
    int juego_iniciado;
    char palabra_secreta[50];
} EstadoJuego;

EstadoJuego *juego;

void inicializar_juego() {
    juego = mmap(NULL, sizeof(EstadoJuego), PROT_READ | PROT_WRITE, MAP_SHARED | MAP_ANONYMOUS, -1, 0);
    sem_init(&juego->semaforo, 1, 1);
    juego->num_conectados = 0;
    juego->num_listos = 0;
    juego->palabras_listas = 0;
    juego->votos_totales = 0;
    juego->indice_impostor = -1;
    juego->juego_iniciado = 0;
    strcpy(juego->palabra_secreta, "");
    for (int i = 0; i < MAX_JUGADORES; i++) {
        juego->votos[i] = 0;
        strcpy(juego->nombres[i], "");
        strcpy(juego->chat_palabras[i], "");
    }
}

int validar_credenciales(const char *usuario_input, const char *pass_input) {
    FILE *fp = fopen("usuarios.txt", "r");
    if (fp == NULL) return 0;

    char linea[150], db_user[50], db_pass[50];
    while (fgets(linea, sizeof(linea), fp)) {
        linea[strcspn(linea, "\r")] = 0;
        linea[strcspn(linea, "\n")] = 0;

        char *token = strtok(linea, ":");
        if (token != NULL) {
            strcpy(db_user, token);
            token = strtok(NULL, ":");
            if (token != NULL) {
                strcpy(db_pass, token);
                if (strcmp(usuario_input, db_user) == 0 && strcmp(pass_input, db_pass) == 0) {
                    fclose(fp);
                    return 1;
                }
            }
        }
    }
    fclose(fp);
    return 0;
}

int main() {
    int sd, sd_actual;
    struct sockaddr_in sind, pin;
    socklen_t addrlen = sizeof(pin);

    inicializar_juego();

    if ((sd = socket(AF_INET, SOCK_STREAM, 0)) == -1) { perror("Error socket"); exit(1); }
    int opt = 1;
    setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sind.sin_family = AF_INET;
    sind.sin_addr.s_addr = INADDR_ANY;
    sind.sin_port = htons(PUERTO);

    if (bind(sd, (struct sockaddr *)&sind, sizeof(sind)) == -1) { perror("Error bind"); exit(1); }
    if (listen(sd, 10) == -1) { perror("Error listen"); exit(1); }

    printf("Servidor del 'Impostor' iniciado en puerto %d...\n", PUERTO);

    while (1) {
        if ((sd_actual = accept(sd, (struct sockaddr *)&pin, &addrlen)) == -1) continue;

        if (fork() == 0) {
            close(sd);
            char buffer[1024] = {0}, mi_nombre[50] = {0}, mi_pass[50] = {0};
            int mi_id = -1;

            recv(sd_actual, buffer, sizeof(buffer), 0);
            if (strncmp(buffer, "LOGIN:", 6) == 0) {
                char *token = strtok(buffer + 6, ":");
                if (token != NULL) {
                    strcpy(mi_nombre, token);
                    token = strtok(NULL, ":");
                    if (token != NULL) strcpy(mi_pass, token);
                }

                if (!validar_credenciales(mi_nombre, mi_pass)) {
                    send(sd_actual, "ERROR:Credenciales incorrectas.", 32, 0);
                    close(sd_actual);
                    exit(0);
                }

                sem_wait(&juego->semaforo);
                if (juego->num_conectados < MAX_JUGADORES) {
                    mi_id = juego->num_conectados;
                    strcpy(juego->nombres[mi_id], mi_nombre);
                    juego->num_conectados++;
                    sem_post(&juego->semaforo);
                    send(sd_actual, "OK:Autenticado.", 15, 0);
                } else {
                    sem_post(&juego->semaforo);
                    send(sd_actual, "ERROR:Sala llena.", 17, 0);
                    close(sd_actual);
                    exit(0);
                }
            }

            char buf_ready[256] = {0};
            recv(sd_actual, buf_ready, sizeof(buf_ready), 0);
            if (strncmp(buf_ready, "READY", 5) == 0) {
                sem_wait(&juego->semaforo);
                juego->num_listos++;
                if (juego->num_listos == juego->num_conectados && juego->num_conectados >= 2 && juego->juego_iniciado == 0) {
                    srand(time(NULL) ^ getpid());
                    juego->indice_impostor = rand() % juego->num_conectados;

                    int indice_palabra = rand() % num_palabras;
                    strcpy(juego->palabra_secreta, banco_palabras[indice_palabra]);

                    juego->juego_iniciado = 1;
                }
                sem_post(&juego->semaforo);
            }

            while (juego->juego_iniciado == 0) { sleep(1); }

            char mensaje_rol[150] = {0};
            if (mi_id == juego->indice_impostor) {
                strcpy(mensaje_rol, "ROLE:¡ERES EL IMPOSTOR! Engaña a los demás.");
            } else {
                sprintf(mensaje_rol, "ROLE:La palabra es [%s]. Encuentra al impostor.", juego->palabra_secreta);
            }
            send(sd_actual, mensaje_rol, strlen(mensaje_rol), 0);

            char buf_word[256] = {0};
            recv(sd_actual, buf_word, sizeof(buf_word), 0);
            if (strncmp(buf_word, "WORD:", 5) == 0) {
                sem_wait(&juego->semaforo);
                sprintf(juego->chat_palabras[mi_id], "[%s]: %s", mi_nombre, buf_word + 5);
                juego->palabras_listas++;
                sem_post(&juego->semaforo);
            }

            while (juego->palabras_listas < juego->num_conectados) { sleep(1); }

            char chat_completo[1024] = "CHAT_LOG:\n";
            for (int i = 0; i < juego->num_conectados; i++) {
                strcat(chat_completo, juego->chat_palabras[i]);
                strcat(chat_completo, "\n");
            }
            send(sd_actual, chat_completo, strlen(chat_completo), 0);

            sleep(1);
            char lista_jugadores[512] = "VOTE_REQ:";
            for (int i = 0; i < juego->num_conectados; i++) {
                char temp[64];
                sprintf(temp, "%d-%s,", i, juego->nombres[i]);
                strcat(lista_jugadores, temp);
            }
            send(sd_actual, lista_jugadores, strlen(lista_jugadores), 0);

            char buf_vote[256] = {0};
            recv(sd_actual, buf_vote, sizeof(buf_vote), 0);
            if (strncmp(buf_vote, "VOTE:", 5) == 0) {
                int voto_id = atoi(buf_vote + 5);
                sem_wait(&juego->semaforo);
                if (voto_id >= 0 && voto_id < juego->num_conectados) {
                    juego->votos[voto_id]++;
                }
                juego->votos_totales++;
                sem_post(&juego->semaforo);
            }

            while (juego->votos_totales < juego->num_conectados) { sleep(1); }

            int max_votos = -1, expulsado_id = -1;
            for (int i = 0; i < juego->num_conectados; i++) {
                if (juego->votos[i] > max_votos) {
                    max_votos = juego->votos[i];
                    expulsado_id = i;
                }
            }

            char veredicto[256] = {0};
            if (expulsado_id == juego->indice_impostor) {
                sprintf(veredicto, "RESULTADO:¡Ganan los Civiles! El impostor era %s.", juego->nombres[juego->indice_impostor]);
            } else {
                sprintf(veredicto, "RESULTADO:¡Gana el Impostor! El impostor era %s.", juego->nombres[juego->indice_impostor]);
            }
            send(sd_actual, veredicto, strlen(veredicto), 0);

            sleep(2);
            close(sd_actual);
            exit(0);
        }
        close(sd_actual);
    }
    return 0;
}