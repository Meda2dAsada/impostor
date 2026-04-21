import socket

SERVER_IP = 'localhost'
SERVER_PORT = 15000


def main():
    print("=======================================")
    print("   BIENVENIDO A THE IMPOSTOR TCP (Nombre Provisional en lo que encontramos uno bueno  ")
    print("=======================================\n")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((SERVER_IP, SERVER_PORT))
    except Exception as e:
        print(f"[Error]: {e}")
        return

    username = input("Usuario: ").strip()
    password = input("Contraseña: ").strip()

    sock.send(f"LOGIN:{username}:{password}".encode('utf-8'))
    auth_response = sock.recv(1024).decode('utf-8')

    if "ERROR:" in auth_response:
        print(f"Error: {auth_response[6:]}")
        return

    input("\nPresiona Enter y escribe 'ok' para estar listo: ")
    sock.send("READY".encode('utf-8'))
    print("Esperando inicio...")

    while True:
        try:
            data = sock.recv(2048).decode('utf-8')
            if not data: break

            if "ROLE:" in data:
                role_index = data.find("ROLE:")
                # Limpiar si vienen otros mensajes pegados
                texto_rol = data[role_index + 5:].split('WORD:')[0].split('CHAT_LOG:')[0].strip()
                print("\n" + "=" * 50)
                print(f" MISIÓN: {texto_rol}")
                print("=" * 50 + "\n")

                desc = input("Escribe una palabra para describir tu pista: ").strip()
                sock.send(f"WORD:{desc}".encode('utf-8'))
                print("Esperando las descripciones de los demás...")

            if "CHAT_LOG:" in data:
                log_index = data.find("CHAT_LOG:")
                chat_content = data[log_index + 9:].split('VOTE_REQ:')[0].strip()
                print("\n💬 REGISTRO DEL CHAT:")
                print(chat_content)
                print("-" * 50)

            if "VOTE_REQ:" in data:
                req_index = data.find("VOTE_REQ:")
                lista_cruda = data[req_index + 9:].split('RESULTADO:')[0]
                jugadores = [j for j in lista_cruda.split(',') if j.strip()]

                print("\n🗳️ FASE DE VOTACIÓN:")
                for j in jugadores:
                    partes = j.split('-')
                    if len(partes) == 2: print(f" [{partes[0]}] {partes[1]}")

                voto = input("\nID a expulsar: ").strip()
                sock.send(f"VOTE:{voto}".encode('utf-8'))

            if "RESULTADO:" in data:
                res_index = data.find("RESULTADO:")
                print("\n🏆 " + data[res_index + 10:])
                break

        except Exception as e:
            print(f"Error: {e}")
            break

    sock.close()


if __name__ == '__main__':
    main()