# -*- coding: utf-8 -*-
# @Author: William Berge Groensberg
# Automatisk server-finding via LAN broadcast

import socket
import threading
import time

PORT = 5000  # TCP port serveren bruker
BROADCAST_PORT = 5001  # UDP broadcast port

def discover_server(timeout=5):
    """
    Sender UDP broadcast for å finne server på LAN
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.settimeout(timeout)
    message = b"DISCOVER_SERVER"

    # Broadcast til subnet (her 255 for hele subnet)
    client.sendto(message, ("255.255.255.255", BROADCAST_PORT))

    try:
        data, addr = client.recvfrom(1024)
        if data.decode("utf-8") == "SERVER_HERE":
            print(f"[Klient] Fant server på {addr[0]}")
            return addr[0]
    except socket.timeout:
        print("[Klient] Fant ingen server på LAN.")
        return None

def receive(sock):
    while True:
        try:
            msg = sock.recv(1024).decode("utf-8")
            if msg:
                print(msg)
        except:
            print("[Klient] Mistet forbindelsen.")
            break

def main():
    server_ip = discover_server()
    if not server_ip:
        print("Kan ikke koble til server.")
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((server_ip, PORT))
    print(f"[Klient] Koble til server {server_ip}:{PORT}")

    threading.Thread(target=receive, args=(sock,), daemon=True).start()

    while True:
        msg = input("")
        sock.sendall(msg.encode("utf-8"))

if __name__ == "__main__":
    main()
