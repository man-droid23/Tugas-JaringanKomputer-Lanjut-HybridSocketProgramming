import socket
import threading
import struct

HOST = "0.0.0.0"
PORT = 12000
HEADER_SIZE = 4


def recv_exact(sock, num_bytes):
    """
    Menerima tepat sejumlah byte yang diminta.
    Diperlukan karena recv() pada TCP tidak menjamin
    seluruh data diterima dalam satu kali pemanggilan.
    """
    data = b""

    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))

        if not packet:
            return None

        data += packet

    return data


def receive_message(sock):
    """
    Format frame:
    [4-byte message length][message bytes]
    """

    header = recv_exact(sock, HEADER_SIZE)

    if header is None:
        return None

    message_length = struct.unpack("!I", header)[0]

    message = recv_exact(sock, message_length)

    if message is None:
        return None

    return message.decode("utf-8")


def send_message(sock, message):
    message_bytes = message.encode("utf-8")

    header = struct.pack("!I", len(message_bytes))

    sock.sendall(header + message_bytes)


def handle_client(connection_socket, client_address):
    print(f"[CONNECTED] Client {client_address} connected.")

    try:
        while True:
            message = receive_message(connection_socket)

            if message is None:
                break

            print(f"[MESSAGE] {client_address}: {message}")

            if message.lower() == "exit":
                send_message(
                    connection_socket,
                    "Connection closed by server."
                )
                break

            response = f"Server received: {message}"

            send_message(connection_socket, response)

    except ConnectionResetError:
        print(f"[ERROR] Connection reset by {client_address}")

    except Exception as error:
        print(f"[ERROR] {client_address}: {error}")

    finally:
        connection_socket.close()

        print(
            f"[DISCONNECTED] Client {client_address} disconnected."
        )


def start_server():
    # Welcoming socket
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    # Memungkinkan port digunakan kembali setelah server berhenti
    server_socket.setsockopt(
        socket.SOL_SOCKET,
        socket.SO_REUSEADDR,
        1
    )

    server_socket.bind((HOST, PORT))

    # Server mulai listening
    server_socket.listen()

    print(f"[STARTED] TCP Server listening on port {PORT}")
    print("[WAITING] Waiting for clients...")

    try:
        while True:

            # accept() menghasilkan connection socket baru
            connection_socket, client_address = (
                server_socket.accept()
            )

            # Thread terpisah untuk setiap client
            client_thread = threading.Thread(
                target=handle_client,
                args=(
                    connection_socket,
                    client_address
                ),
                daemon=True
            )

            client_thread.start()

            print(
                "[ACTIVE CONNECTIONS]",
                threading.active_count() - 1
            )

    except KeyboardInterrupt:
        print("\n[STOPPING] Server stopped.")

    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
