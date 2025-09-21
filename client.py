# -*- coding: utf-8 -*-
# @Author: William Berge Groensberg
# Automatisk server-finding via LAN broadcast (flere valg + disconnect + reconnect)

import socket
import threading
import time
import sys
import os

PORT = 5000            # TCP port serveren bruker
BROADCAST_PORT = 5001  # UDP broadcast port

def discover_servers(timeout=3):
    """Sender UDP broadcast og samler svar fra alle servere på LAN"""
    servers = []
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.settimeout(timeout)

    message = b"DISCOVER_SERVER"
    client.sendto(message, ("255.255.255.255", BROADCAST_PORT))

    start = time.time()
    while time.time() - start < timeout:
        try:
            data, addr = client.recvfrom(1024)
            if data.decode("utf-8") == "SERVER_HERE":
                if addr[0] not in servers:
                    servers.append(addr[0])
        except socket.timeout:
            break

    client.close()
    return servers

def choose_server():
    servers = discover_servers()
    if not servers:
        print("[Klient] Fant ingen servere på LAN.")
        return None

    if len(servers) == 1:
        print(f"[Klient] Fant én server: {servers[0]}")
        return servers[0]

    print("\nTilgjengelige servere:")
    for i, s in enumerate(servers, 1):
        print(f"{i}. {s}")

    while True:
        try:
            choice = int(input("\nVelg servernummer: "))
            if 1 <= choice <= len(servers):
                return servers[choice - 1]
        except ValueError:
            pass
        print("Ugyldig valg, prøv igjen.")

def receive(sock):
    """Mottar meldinger fra serveren"""
    while True:
        try:
            msg = sock.recv(1024).decode("utf-8")
            if not msg:
                print("[Klient] Forbindelsen ble lukket av serveren.")
                break
            print(msg)
        except:
            print("[Klient] Mistet forbindelsen.")
            break
    # signaler at mottakeren er død
    return

def run_client():
    """Starter én klientforbindelse. Returnerer False hvis brukeren skrev /stop"""
    server_ip = choose_server()
    if not server_ip:
        time.sleep(3)
        return True  # prøv igjen med discovery

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((server_ip, PORT))
    except Exception as e:
        print(f"[Klient] Klarte ikke koble til {server_ip}:{PORT} ({e})")
        time.sleep(3)
        return True  # prøv å reconnecte

    print(f"[Klient] Koblet til server {server_ip}:{PORT}")

    # start mottakertråd
    t = threading.Thread(target=receive, args=(sock,), daemon=True)
    t.start()

    while True:
        try:
            msg = input("")
            if msg.strip().lower() == "/stop":
                print("[Klient] Kobler fra og avslutter...")
                sock.close()
                return False  # slutt helt
            sock.sendall(msg.encode("utf-8"))
        except:
            print("[Klient] Mistet forbindelsen til serveren.")
            break

    # hvis vi mister kontakt → prøv igjen
    time.sleep(3)
    return True

def main():
    while True:
        keep_running = run_client()
        if not keep_running:
            break
        print("[Klient] Prøver å finne server på nytt...")

if __name__ == "__main__":
    main()
