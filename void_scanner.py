import socket
import os
import time
import sys
import math

# =========================
# VISUAL ENGINE
# =========================
def rgb_text(text, offset):
    colored_chars = []
    FREQ = 0.1
    for i, char in enumerate(text):
        if char == "\n":
            colored_chars.append("\n")
            continue
        r = int(math.sin(FREQ * i + offset) * 127 + 128)
        g = int(math.sin(FREQ * i + offset + 2) * 127 + 128)
        b = int(math.sin(FREQ * i + offset + 4) * 127 + 128)
        colored_chars.append(f"\033[38;2;{r};{g};{b}m{char}")
    return "".join(colored_chars) + "\033[0m"

def get_logo():
    return r"""
 ░▒▓██████▓▒░      ▄▄██████▄▄      ░▒▓██████▓▒░
 ░▒▓██▓▒░        ▄████████████▄        ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▀▄ ▓▓ ▄▀ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▓▓ ▼▼ ▓▓ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░        ▀████████████▀        ░▒▓██▓▒░
  ░▒▓██▓▒░         ▀▀██████▀▀         ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║    V  O  I  D     T  E  A  M     ║
        ╚══════════════════════════════════╝
           [ VOID-SCANNER :: ELITE v4 ]
    """

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def flush_stdin():
    """Bersihkan buffer stdin agar input sisa tidak terbaca"""
    if sys.platform.startswith('win'):
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    else:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)

def spinner(label, duration=0.5):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        sys.stdout.write(f"\r\033[1;33m {frames[i % len(frames)]} {label}\033[0m")
        sys.stdout.flush()
        time.sleep(0.05)
        i += 1
    sys.stdout.write("\r" + " " * (len(label)+8) + "\r")

# =========================
# CORE ENGINE
# =========================
def run_scanner(key):
    if key != "VOID_ACCESS_GRANTED_2026":
        print("\033[1;31m[!] ILLEGAL ACCESS DETECTED!\033[0m")
        time.sleep(2)
        return

    flush_stdin()  # penting: bersihkan input sisa dari menu utama

    clear_screen()
    print(rgb_text(get_logo(), 5))
    print("\n\033[1;36m [ STATUS: ENGINE READY ]\033[0m")
    print("\033[1;30m ==================================\033[0m")

    while True:  # loop utama untuk scan berturut-turut
        # ===== INPUT TARGET =====
        while True:
            print("\033[1;33m [?] Masukkan Target Domain")
            print(" [0] Kembali ke Menu Utama")
            target = input(" >>> \033[1;37m").strip()
            print("\033[0m")

            if target == "0":
                return  # balik ke menu utama

            if not target:
                print("\n\033[1;31m [!] Target tidak boleh kosong!\033[0m\n")
                continue
            break  # target valid

        start_time = time.time()

        try:
            spinner("Resolving domain")
            ip_address = socket.gethostbyname(target)

            print(f"\033[1;32m [+] TARGET      : {target}\033[0m")
            print(f"\033[1;36m [+] IP ADDRESS : {ip_address}\033[0m")

            # Reverse DNS
            try:
                rdns = socket.gethostbyaddr(ip_address)[0]
                print(f"\033[1;35m [+] rDNS       : {rdns}\033[0m")
            except Exception:
                print(f"\033[1;30m [+] rDNS       : Not Available\033[0m")

            print("\033[1;30m ----------------------------------\033[0m")
            print("\033[1;36m [ STATUS: SCANNING PORTS ]\033[0m\n")

            ports = {21:"FTP",22:"SSH",80:"HTTP",443:"HTTPS",3306:"MySQL"}
            open_ports = []

            for port, service in ports.items():
                spinner(f"Checking {service} ({port})")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                try:
                    if sock.connect_ex((ip_address, port)) == 0:
                        open_ports.append(port)
                        print(f" \033[1;32m[OPEN ] {port:<5} {service}\033[0m")
                    else:
                        print(f" \033[1;30m[CLOSE] {port:<5} {service}\033[0m")
                finally:
                    sock.close()

            duration = time.time() - start_time

            # ===== SUMMARY =====
            print("\n\033[1;30m ==================================\033[0m")
            print("\033[1;36m [ SCAN SUMMARY ]\033[0m")
            print(f" \033[1;32m Open Ports  : {len(open_ports)}\033[0m")
            print(f" \033[1;30m Closed Port : {len(ports)-len(open_ports)}\033[0m")
            print(f" \033[1;35m Duration    : {duration:.2f}s\033[0m")

        except socket.gaierror:
            print(f"\n\033[1;31m [!] Domain '{target}' tidak valid.\033[0m")
        except KeyboardInterrupt:
            print("\n\033[1;31m [!] Scan dibatalkan.\033[0m")

        # ===== POST ACTION =====
        while True:
            print("\n\033[1;33m [1] Scan target lain")
            print(" [0] Kembali ke Menu Utama\033[0m")
            choice = input(" >>> ").strip()
            if choice == "1":
                break  # ulang loop scan → target lain
            elif choice == "0":
                return
            else:
                print("\033[1;31m [!] Pilihan tidak valid.\033[0m")
