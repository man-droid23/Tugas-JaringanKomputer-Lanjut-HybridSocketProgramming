import socket
import struct

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12000
HEADER_SIZE = 4


def recv_exact(sock, num_bytes):
    data = b""

    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))

        if not packet:
            return None

        data += packet

    return data


def receive_message(sock):
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

    header = struct.pack(
        "!I",
        len(message_bytes)
    )

    sock.sendall(header + message_bytes)


def start_client():
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    try:
        client_socket.connect(
            (SERVER_HOST, SERVER_PORT)
        )

        print(
            f"[CONNECTED] Connected to "
            f"{SERVER_HOST}:{SERVER_PORT}"
        )

        while True:
            message = input("Message: ")

            send_message(
                client_socket,
                message
            )

            response = receive_message(
                client_socket
            )

            if response is None:
                print(
                    "[DISCONNECTED] Server closed connection."
                )
                break

            print(f"Server: {response}")

            if message.lower() == "exit":
                break

    except ConnectionRefusedError:
        print(
            "[ERROR] Cannot connect to server."
        )

    except KeyboardInterrupt:
        print("\n[STOPPED] Client stopped.")

    finally:
        client_socket.close()


if __name__ == "__main__":
    start_client()
