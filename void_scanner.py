import socket
import os
import time
import sys
import math
import threading
from queue import Queue

# =========================
# VISUAL ENGINE
# =========================
def rgb_text(text, offset=0):
    FREQ = 0.08
    out = []
    for i, c in enumerate(text):
        if c == "\n":
            out.append("\n")
            continue
        r = int(math.sin(FREQ * i + offset) * 127 + 128)
        g = int(math.sin(FREQ * i + offset + 2) * 127 + 128)
        b = int(math.sin(FREQ * i + offset + 4) * 127 + 128)
        out.append(f"\033[38;2;{r};{g};{b}m{c}")
    return "".join(out) + "\033[0m"


def logo():
    return r"""
 ░▒▓██████▓▒░      ▄▄██████▄▄      ░▒▓██████▓▒░
 ░▒▓██▓▒░        ▄████████████▄        ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▀▄ ▓▓ ▄▀ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▓▓ ▼▼ ▓▓ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░        ▀████████████▀        ░▒▓██▓▒░
  ░▒▓██▓▒░         ▀▀██████▀▀         ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║     V O I D   S C A N N E R      ║
        ╚══════════════════════════════════╝
             [ LEVEL C / X MAX ]
    """


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def flush_input():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        pass


# =========================
# SCAN ENGINE
# =========================
SMART_PORTS = {
    21: "FTP", 22: "SSH", 23: "TELNET", 25: "SMTP",
    53: "DNS", 80: "HTTP", 110: "POP3", 143: "IMAP",
    443: "HTTPS", 445: "SMB", 8080: "HTTP-ALT",
    8443: "HTTPS-ALT", 3306: "MYSQL", 3389: "RDP"
}

TIMEOUT_FAST = 0.3
TIMEOUT_STEALTH = 0.8
THREADS = 80


def scan_port(ip, port, timeout, results):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        if s.connect_ex((ip, port)) == 0:
            results.append(port)
    finally:
        s.close()


def threaded_scan(ip, ports, timeout):
    results = []
    q = Queue()

    for p in ports:
        q.put(p)

    def worker():
        while not q.empty():
            port = q.get()
            scan_port(ip, port, timeout, results)
            q.task_done()

    for _ in range(min(THREADS, len(ports))):
        threading.Thread(target=worker, daemon=True).start()

    q.join()
    return sorted(results)


# =========================
# MAIN MODULE
# =========================
def run_scanner(key):
    if key != "VOID_ACCESS_GRANTED_2026":
        print("\033[1;31m[!] ILLEGAL ACCESS\033[0m")
        return

    clear()
    print(rgb_text(logo(), 5))

    while True:
        flush_input()
        print("\n\033[1;36m[ SCAN MODE ]\033[0m")
        print(" 1. FAST SCAN (Quick Recon)")
        print(" 2. STEALTH SCAN (Silent)")
        print(" 0. Back to Menu")

        mode = input("\n Select mode: ").strip()

        if mode == "0":
            return
        if mode not in ("1", "2"):
            continue

        timeout = TIMEOUT_FAST if mode == "1" else TIMEOUT_STEALTH

        while True:
            flush_input()
            target = input("\n Target domain / IP (0 back): ").strip()
            if target == "0":
                break
            if not target:
                continue

            try:
                ip = socket.gethostbyname(target)
            except:
                print("\033[1;31m[!] Invalid target\033[0m")
                continue

            print(f"\n\033[1;32m[+] TARGET : {target}\033[0m")
            print(f"\033[1;36m[+] IP     : {ip}\033[0m")

            try:
                rdns = socket.gethostbyaddr(ip)[0]
                print(f"\033[1;35m[+] rDNS   : {rdns}\033[0m")
            except:
                pass

            ports = list(SMART_PORTS.keys())
            start = time.time()

            print("\n\033[1;33m[+] SCANNING...\033[0m")
            open_ports = threaded_scan(ip, ports, timeout)

            print("\n\033[1;36m[ RESULT ]\033[0m")
            for p in ports:
                if p in open_ports:
                    print(f" \033[1;32mOPEN   {p:<5} {SMART_PORTS[p]}\033[0m")
                else:
                    print(f" \033[1;30mCLOSE  {p:<5} {SMART_PORTS[p]}\033[0m")

            dur = time.time() - start
            print(f"\n\033[1;35mDuration: {dur:.2f}s\033[0m")

            print("\n 1. Scan another target")
            print(" 2. Export result (TXT)")
            print(" 0. Back")

            choice = input("\n Select: ").strip()

            if choice == "2":
                fname = f"scan_{ip.replace('.', '_')}.txt"
                with open(fname, "w") as f:
                    f.write(f"TARGET: {target}\nIP: {ip}\n\n")
                    for p in open_ports:
                        f.write(f"OPEN {p} {SMART_PORTS[p]}\n")
                print(f"\033[1;32m[+] Saved: {fname}\033[0m")

            if choice == "0":
                break


if __name__ == "__main__":
    print("[!] Load from login.py only")
