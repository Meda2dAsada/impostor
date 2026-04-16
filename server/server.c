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
#define MAX_JUGADORES 10
#define JUGADORES_PARA_INICIAR 2

typedef struct {
    sem_t semaforo;
    int num_conectados;
    char nombres[MAX_JUGADORES][50];
    int votos[MAX_JUGADORES];
    int indice_impostor;
    int juego_iniciado;
    char palabra_secreta[50];
} EstadoJuego;

EstadoJuego *juego;

void inicializar_juego() {
    juego = mmap(NULL, sizeof(EstadoJuego), PROT_READ | PROT_WRITE,
                 MAP_SHARED | MAP_ANONYMOUS, -1, 0);

    sem_init(&juego->semaforo, 1, 1);

    juego->num_conectados = 0;
    juego->indice_impostor = -1;
    juego->juego_iniciado = 0;
    strcpy(juego->palabra_secreta, "");

    for (int i = 0; i < MAX_JUGADORES; i++) {
        juego->votos[i] = 0;
        strcpy(juego->nombres[i], "");
    }
}

int main() {
    int sd, sd_actual;
    struct sockaddr_in sind, pin;
    socklen_t addrlen = sizeof(pin);

    inicializar_juego();

    if ((sd = socket(AF_INET, SOCK_STREAM, 0)) == -1) {
        perror("Error al crear socket");
        exit(1);
    }

    int opt = 1;
    setsockopt(sd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sind.sin_family = AF_INET;
    sind.sin_addr.s_addr = INADDR_ANY;
    sind.sin_port = htons(PUERTO);

    if (bind(sd, (struct sockaddr *)&sind, sizeof(sind)) == -1) {
        perror("Error en bind");
        exit(1);
    }

    if (listen(sd, 10) == -1) {
        perror("Error en listen");
        exit(1);
    }

    printf("Servidor del 'Impostor' iniciado en el puerto %d...\n", PUERTO);
    printf("Esperando jugadores para iniciar...\n");

    while (1) {
        if ((sd_actual = accept(sd, (struct sockaddr *)&pin, &addrlen)) == -1) {
            continue;
        }

        if (fork() == 0) {
            close(sd);

            char buffer[1024] = {0};
            char mi_nombre[50] = {0};
            int mi_id = -1;

            recv(sd_actual, buffer, sizeof(buffer), 0);

            if (strncmp(buffer, "LOGIN:", 6) == 0) {
                strcpy(mi_nombre, buffer + 6);
                mi_nombre[strcspn(mi_nombre, "\n")] = 0;

                sem_wait(&juego->semaforo);

                if (juego->num_conectados < MAX_JUGADORES) {
                    mi_id = juego->num_conectados;
                    strcpy(juego->nombres[mi_id], mi_nombre);
                    juego->num_conectados++;
                    printf("Jugador conectado: %s (ID: %d)\n", mi_nombre, mi_id);

                    if (juego->num_conectados == JUGADORES_PARA_INICIAR && juego->juego_iniciado == 0) {
                        printf("\n>>> ¡Sala llena! Configurando partida...\n");

                        srand(time(NULL) ^ getpid());
                        juego->indice_impostor = rand() % JUGADORES_PARA_INICIAR;

                        strcpy(juego->palabra_secreta, "Hamburguesa");

                        juego->juego_iniciado = 1;
                    }

                    sem_post(&juego->semaforo);

                    send(sd_actual, "OK: Bienvenido al Lobby. Esperando jugadores...", 47, 0);
                } else {
                    sem_post(&juego->semaforo);
                    send(sd_actual, "ERROR: Sala llena", 17, 0);
                    close(sd_actual);
                    exit(0);
                }
            } else {
                send(sd_actual, "ERROR: Comando invalido. Usa LOGIN:nombre", 40, 0);
                close(sd_actual);
                exit(0);
            }

            while (juego->juego_iniciado == 0) {
                sleep(1);
            }

            char mensaje_rol[150] = {0};
            if (mi_id == juego->indice_impostor) {
                strcpy(mensaje_rol, "ROLE:¡ERES EL IMPOSTOR! Finge que sabes de que hablan.");
            } else {
                sprintf(mensaje_rol, "ROLE:La palabra secreta es [%s]. Descubre al impostor.", juego->palabra_secreta);
            }

            send(sd_actual, mensaje_rol, strlen(mensaje_rol), 0);
            printf("Rol enviado al jugador %s (ID: %d)\n", mi_nombre, mi_id);

            sleep(20);

            close(sd_actual);
            exit(0);
        }

        close(sd_actual);
    }

    return 0;
}