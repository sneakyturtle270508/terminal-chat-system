# -*- coding: utf-8 -*-
# @Author: William Berge Groensberg
# @Date:   2025-09-19 17:25:56
# @Last Modified by:   William Berge Groensberg
# @Last Modified time: 2025-09-20 14:47:53
import socket
import threading
import os
import time

HOST = "0.0.0.0"
PORT = 5000
BROADCAST_PORT = 5001  # For automatisk discovery

rooms = {}  # {pin: [{"conn": conn, "name": name}, ...]}
lock = threading.Lock()
log = []  # siste hendelser
MAX_LOG = 10

server_running = True
server_active = False    # True = kan akseptere nye klienter
server_stopped = False   # True = meldinger blokkert, ingen kick mulig

# -------------------
# Logg-håndtering
# -------------------
def add_log(entry):
    global log
    log.append(entry)
    if len(log) > MAX_LOG:
        log = log[-MAX_LOG:]

# -------------------
# UDP discovery (LAN)
# -------------------
def udp_discovery():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", BROADCAST_PORT))
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            if data.decode("utf-8") == "DISCOVER_SERVER":
                sock.sendto(b"SERVER_HERE", addr)
        except:
            break

threading.Thread(target=udp_discovery, daemon=True).start()

# -------------------
# Dashboard
# -------------------
def print_dashboard(show_help=False):
    if not show_help:
        os.system("cls")
    print("=== SERVER DASHBOARD ===")
    print(f"Server aktiv for nye klienter: {server_active}")
    print(f"Server stoppet (meldinger blokkert): {server_stopped}")
    if rooms:
        for pin, users in rooms.items():
            print(f"Rom {pin}: {[u['name'] for u in users]}")
    else:
        print("Ingen aktive rom.")
    if show_help:
        print("""
Kommandoer:
  /start                   Start serveren (ny klienter og meldinger OK)
  /standby                 Sett server i standby (ingen nye klienter)
  /stop                    Stop server midlertidig (blokker meldinger + nye klienter)
  /stop server              Stopp hele serveren
  /room <PIN>              Lukk et rom
  /room <PIN> <spiller>    Kaste ut en spiller
  /logg                    Vis siste hendelser
  /help                    Vis denne hjelpen
""")
    else:
        print("\nSkriv /help for kommandoer.\n")

# -------------------
# Broadcast meldinger til rom
# -------------------
def broadcast(message, pin):
    if pin in rooms:
        for user in rooms[pin]:
            try:
                user["conn"].sendall(message.encode("utf-8"))
            except:
                rooms[pin].remove(user)

# -------------------
# Håndtere klient
# -------------------
def handle_client(conn, addr):
    global server_active, server_stopped
    try:
        if not server_active:
            conn.sendall("[Server] Serveren er i standby. Ingen nye klienter.".encode("utf-8"))
            conn.close()
            return

        conn.sendall("Skriv inn PIN for rommet du vil bli med i: ".encode("utf-8"))
        pin = conn.recv(1024).decode("utf-8").strip()

        conn.sendall("Skriv inn ditt navn: ".encode("utf-8"))
        name = conn.recv(1024).decode("utf-8").strip()

        with lock:
            if pin not in rooms:
                rooms[pin] = []
            rooms[pin].append({"conn": conn, "name": name})
            add_log(f"{name} koblet til rom {pin}")

        broadcast(f"[Server] {name} har koblet til rom {pin}", pin)
        print_dashboard()

        while True:
            msg = conn.recv(1024).decode("utf-8")
            if not msg:
                break
            if server_stopped:
                conn.sendall("[Server] Serveren er stoppet. Meldinger er deaktivert.".encode("utf-8"))
                continue
            broadcast(f"{name}: {msg}", pin)
    except:
        pass

    with lock:
        if pin in rooms:
            rooms[pin] = [u for u in rooms[pin] if u["conn"] != conn]
            if not rooms[pin]:
                del rooms[pin]
            broadcast(f"[Server] {name} har forlatt rom {pin}", pin)
            add_log(f"{name} forlot rom {pin}")
            print_dashboard()
    conn.close()

# -------------------
# Akseptere nye klienter
# -------------------
def client_accept_loop(server):
    global server_running
    while server_running:
        try:
            server.settimeout(1.0)
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue

# -------------------
# Kommando-loop
# -------------------
def command_loop():
    global server_running, server_active, server_stopped
    while server_running:
        print_dashboard()
        cmd = input("Server> ").strip()
        if cmd.lower() == "/start":
            server_active = True
            server_stopped = False
            print("[Server] Serveren startet. Nye klienter og meldinger OK.")
            add_log("Server startet")
        elif cmd.lower() == "/standby":
            server_active = False
            print("[Server] Serveren i standby. Ingen nye klienter.")
            add_log("Server i standby")
        elif cmd.lower() == "/stop":
            server_active = False
            server_stopped = True
            print("[Server] Server stoppet midlertidig. Meldinger og nye klienter blokkert.")
            add_log("Server stoppet midlertidig")
        elif cmd.lower() == "/stop server":
            server_running = False
            print("[Server] Stopper hele serveren og lukker alle tilkoblinger...")
            add_log("Server stoppet helt")
            break
        elif cmd.lower() == "/help":
            print_dashboard(show_help=True)
            input("Trykk Enter for å gå tilbake til dashboard...")
        elif cmd.lower() == "/logg":
            os.system("cls")
            print("=== SISTE HENDELSER ===")
            for entry in log:
                print(entry)
            input("\nTrykk Enter for å gå tilbake til dashboard...")
        elif cmd.lower().startswith("/room "):
            parts = cmd.split()
            with lock:
                if server_stopped:
                    print("[Server] Kan ikke administrere rom mens serveren er stoppet.")
                    continue
                if len(parts) == 2:
                    pin = parts[1]
                    if pin in rooms:
                        for u in rooms[pin]:
                            try:
                                u["conn"].sendall("[Server] Rommet er lukket.".encode("utf-8"))
                                u["conn"].close()
                            except:
                                pass
                        del rooms[pin]
                        print(f"[Server] Rom {pin} lukket.")
                        add_log(f"Rom {pin} lukket")
                    else:
                        print(f"[Server] Rom {pin} finnes ikke.")
                elif len(parts) == 3:
                    pin, player = parts[1], parts[2]
                    if pin in rooms:
                        found = False
                        for u in rooms[pin]:
                            if u["name"] == player:
                                try:
                                    u["conn"].sendall("[Server] Du har blitt kastet ut.".encode("utf-8"))
                                    u["conn"].close()
                                except:
                                    pass
                                rooms[pin].remove(u)
                                found = True
                                break
                        if not rooms[pin]:
                            del rooms[pin]
                        if found:
                            print(f"[Server] Spiller {player} kastet ut fra rom {pin}.")
                            add_log(f"Spiller {player} kastet ut fra rom {pin}")
                        else:
                            print(f"[Server] Fant ikke spiller {player} i rom {pin}.")
                    else:
                        print(f"[Server] Rom {pin} finnes ikke.")
        time.sleep(0.1)

# -------------------
# Main
# -------------------
def main():
    global server_running
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print("Server klar. Bruk /start for å aktivere. /help for kommandoer.")

    threading.Thread(target=client_accept_loop, args=(server,), daemon=True).start()
    command_loop()

    # Lukk alle tilkoblinger
    with lock:
        for pin_users in rooms.values():
            for u in pin_users:
                try:
                    u["conn"].close()
                except:
                    pass
        rooms.clear()
    server.close()
    print("Server stoppet.")
    

if __name__ == "__main__":
    main()
