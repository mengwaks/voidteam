import socket
import os
import time
import sys
import math # Penting untuk hitungan warna RGB

# --- FUNGSI TAMPILAN (Agar sama mewahnya dengan login.py) ---
def rgb_text(text, offset):
    colored_chars = []
    FREQ = 0.1
    for i, char in enumerate(text):
        if char == '\n':
            colored_chars.append('\n')
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
           [ VOID-SCANNER MODULE ]
    """

def run_scanner(key):
    # 1. Verifikasi Kunci Akses
    if key != "VOID_ACCESS_GRANTED_2026":
        print("\033[1;31m[!] ILLEGAL ACCESS DETECTED!")
        time.sleep(2)
        return 

    os.system('clear')
    
    # Tampilkan Logo RGB Burung Hantu
    print(rgb_text(get_logo(), 5))
    print("\n\033[1;36m [ STATUS: SCANNER ENGINE READY ]\033[0m")
    print("\033[1;30m ==================================\033[0m")
    
    # --- FIX SKIP INPUT ---
    # Memberi jeda sedikit lebih lama agar sisa Enter dari login.py hilang
    time.sleep(0.5) 
    
    try:
        # Prompt input dengan warna
        print("\033[1;33m")
        target = input(" [?] Target Domain (google.com): \033[1;37m").strip()
        print("\033[0m")
        
        if not target:
            print("\n\033[1;31m [!] Error: Target tidak boleh kosong!\033[0m")
        else:
            print(f"\n\033[1;32m [+] Analyzing Target: {target}...\033[0m")
            ip_address = socket.gethostbyname(target)
            print(f"\033[1;36m [+] IP Address FOUND: {ip_address}\033[0m")
            print("\033[1;30m ----------------------------------\033[0m")

            ports = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL"}
            for port, service in ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip_address, port))
                if result == 0:
                    print(f"     \033[1;32m[OPEN] Port {port} : {service}\033[0m")
                else:
                    # Menampilkan port tertutup dengan warna redup
                    print(f"     \033[1;30m[CLOSE] Port {port} : {service}\033[0m")
                sock.close()
            
    except socket.gaierror:
        print(f"\n\033[1;31m [!] Error: Domain '{target}' tidak ditemukan.\033[0m")
    except Exception as e:
        print(f"\n\033[1;31m [!] Error: {e}\033[0m")
    
    # Penahan layar
    print("\n\033[1;30m ==================================\033[0m")
    input("\033[1;37m [✓] Selesai. Tekan Enter untuk kembali ke Menu...\033[0m")

if __name__ == "__main__":
    print("\033[1;31m[!] ERROR: This module must be loaded from login.py\033[0m")
