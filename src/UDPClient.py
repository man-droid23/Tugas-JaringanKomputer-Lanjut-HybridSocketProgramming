import socket
import statistics
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 12001

NUMBER_OF_PINGS = 10
TIMEOUT = 1.0
PING_INTERVAL = 1.0

BUFFER_SIZE = 1024


def start_udp_client():
    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_DGRAM
    )

    # Sesuai requirement tugas
    client_socket.settimeout(TIMEOUT)

    rtt_results = []
    packets_received = 0

    print(
        f"[START] UDP Pinger -> "
        f"{SERVER_HOST}:{SERVER_PORT}"
    )

    print(
        f"[CONFIG] Timeout = {TIMEOUT} second"
    )

    print("-" * 55)

    try:
        for sequence_number in range(
            1,
            NUMBER_OF_PINGS + 1
        ):
            timestamp = time.time()

            message = (
                f"PING|"
                f"{sequence_number}|"
                f"{timestamp}"
            )

            start_time = time.perf_counter()

            client_socket.sendto(
                message.encode("utf-8"),
                (SERVER_HOST, SERVER_PORT)
            )

            try:
                while True:
                    elapsed = (
                        time.perf_counter()
                        - start_time
                    )

                    remaining_timeout = (
                        TIMEOUT - elapsed
                    )

                    if remaining_timeout <= 0:
                        raise socket.timeout

                    client_socket.settimeout(
                        remaining_timeout
                    )

                    response, server_address = (
                        client_socket.recvfrom(
                            BUFFER_SIZE
                        )
                    )

                    response_message = (
                        response.decode("utf-8")
                    )

                    parts = response_message.split("|")

                    if (
                        len(parts) != 3
                        or parts[0] != "PONG"
                    ):
                        print(
                            "[WARNING] Invalid response "
                            "received. Ignoring packet."
                        )
                        continue

                    response_sequence = int(parts[1])

                    # Menghindari delayed UDP packet
                    # dianggap sebagai jawaban ping berikutnya.
                    if response_sequence != sequence_number:
                        print(
                            f"[WARNING] Late packet "
                            f"PONG #{response_sequence} "
                            f"ignored."
                        )
                        continue

                    end_time = time.perf_counter()

                    rtt = (
                        end_time - start_time
                    ) * 1000

                    packets_received += 1
                    rtt_results.append(rtt)

                    print(
                        f"PING {sequence_number:02d}: "
                        f"Reply from "
                        f"{server_address[0]}:"
                        f"{server_address[1]} "
                        f"RTT = {rtt:.3f} ms"
                    )

                    break

            except socket.timeout:
                print(
                    f"PING {sequence_number:02d}: "
                    f"Request timed out "
                    f"(>{TIMEOUT:.1f} s)"
                )

            if sequence_number < NUMBER_OF_PINGS:
                time.sleep(PING_INTERVAL)

    except KeyboardInterrupt:
        print("\n[STOPPED] UDP Client stopped.")

    finally:
        client_socket.close()

    print_statistics(
        rtt_results,
        packets_received
    )


def print_statistics(
    rtt_results,
    packets_received
):
    packets_sent = NUMBER_OF_PINGS
    packets_lost = (
        packets_sent - packets_received
    )

    packet_loss = (
        packets_lost
        / packets_sent
    ) * 100

    print("\n" + "=" * 55)

    print("UDP PING STATISTICS")

    print("=" * 55)

    print(
        f"Packets Sent     : {packets_sent}"
    )

    print(
        f"Packets Received : {packets_received}"
    )

    print(
        f"Packets Lost     : {packets_lost}"
    )

    print(
        f"Packet Loss      : {packet_loss:.1f}%"
    )

    if rtt_results:
        print(
            f"Minimum RTT      : "
            f"{min(rtt_results):.3f} ms"
        )

        print(
            f"Maximum RTT      : "
            f"{max(rtt_results):.3f} ms"
        )

        print(
            f"Average RTT      : "
            f"{statistics.mean(rtt_results):.3f} ms"
        )

    else:
        print(
            "RTT Statistics  : "
            "No response received"
        )


if __name__ == "__main__":
    start_udp_client()
