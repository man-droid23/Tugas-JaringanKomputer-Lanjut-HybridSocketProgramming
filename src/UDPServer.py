import os
import random
import socket

HOST = "0.0.0.0"
PORT = 12001
BUFFER_SIZE = 1024

# Default 0 = tidak ada simulated packet loss.
# Untuk pengujian dapat dijalankan dengan:
# UDP_SIMULATED_LOSS_RATE=0.3 python src/UDPServer.py
SIMULATED_LOSS_RATE = float(
    os.getenv("UDP_SIMULATED_LOSS_RATE", "0")
)


def start_udp_server():
    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    server_socket.bind((HOST, PORT))

    print(
        f"[STARTED] UDP Heartbeat Server "
        f"listening on port {PORT}"
    )

    print(
        f"[CONFIG] Simulated packet loss: "
        f"{SIMULATED_LOSS_RATE * 100:.0f}%"
    )

    try:
        while True:
            data, client_address = server_socket.recvfrom(
                BUFFER_SIZE
            )

            message = data.decode("utf-8")

            print(
                f"[RECEIVED] {client_address}: {message}"
            )

            # Optional: simulasi unreliable delivery UDP.
            if random.random() < SIMULATED_LOSS_RATE:
                print(
                    f"[DROP] Packet from "
                    f"{client_address} intentionally dropped."
                )
                continue

            parts = message.split("|")

            if len(parts) != 3 or parts[0] != "PING":
                print(
                    f"[INVALID] Invalid packet from "
                    f"{client_address}"
                )
                continue

            sequence_number = parts[1]
            client_timestamp = parts[2]

            response = (
                f"PONG|"
                f"{sequence_number}|"
                f"{client_timestamp}"
            )

            server_socket.sendto(
                response.encode("utf-8"),
                client_address
            )

            print(
                f"[SENT] PONG #{sequence_number} "
                f"to {client_address}"
            )

    except KeyboardInterrupt:
        print("\n[STOPPING] UDP Server stopped.")

    finally:
        server_socket.close()


if __name__ == "__main__":
    start_udp_server()
