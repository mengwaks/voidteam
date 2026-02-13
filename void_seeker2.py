import socket
import os
import sys
import time
import math
import threading
import json
import ssl
import urllib.request
from queue import Queue

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

def get_logo():
    return r"""
 ░▒▓██████▓▒░      ▄▄██████▄▄      ░▒▓██████▓▒░
 ░▒▓██▓▒░        ▄████████████▄        ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▀▄ ▓▓ ▄▀ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▓▓ ▼▼ ▓▓ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░        ▀████████████▀        ░▒▓██▓▒░
  ░▒▓██▓▒░         ▀▀██████▀▀         ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║     V O I D - S E E K E R  V3    ║
        ╚══════════════════════════════════╝
           [ OSINT: SSL HISTORY ANALYZER ]
    """

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def flush_input():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        pass

CDN_RANGES = {
    "CLOUDFLARE": ["104.", "172.64.", "172.65.", "172.66.", "172.67.", "108.162.", "162.15.", "190.93.", "198.41."],
    "AKAMAI": ["23.", "104.", "184.", "2.16.", "2.23."],
    "GOOGLE": ["34.", "35.", "104.154.", "104.196."],
    "AWS": ["3.", "13.", "18.", "52.", "54."]
}

def get_provider_status(ip):
    for provider, prefixes in CDN_RANGES.items():
        for prefix in prefixes:
            if ip.startswith(prefix):
                return provider
    return "ORIGIN"

# =========================
# CORE LOGIC
# =========================
def fetch_crt_sh(domain):
    """Mengambil data subdomain dari Certificate Logs"""
    print(f" \033[1;34m[*] Menghubungi Database SSL (crt.sh)...\033[0m")
    subdomains = set()
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        
        with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
            data = json.loads(response.read().decode())
            
        for entry in data:
            name_value = entry['name_value']
            for sub in name_value.split('\n'):
                if "*" not in sub and sub.endswith(domain):
                    subdomains.add(sub)
        
        return list(subdomains)
    except Exception as e:
        print(f" \033[1;31m[!] Gagal mengambil data: {e}\033[0m")
        return []

def worker(q, results, print_lock):
    while not q.empty():
        full_url = q.get()
        
        with print_lock:
            sys.stdout.write(f"\r\033[K \033[1;30m[-] Checking: {full_url[:40]}...\033[0m")
            sys.stdout.flush()
        
        try:
            ip = socket.gethostbyname(full_url)
            status = get_provider_status(ip)
            
            with print_lock:
                if status == "ORIGIN":
                    sys.stdout.write(f"\r\033[K")
                    print(f" \033[1;32m[ORIGIN] {full_url.ljust(35)} -> {ip}\033[0m")
                    results.append((full_url, ip, "ORIGIN"))
                else:
                    
                    sys.stdout.write(f"\r\033[K")
                    print(f" \033[1;33m[{status}] {full_url.ljust(35)} -> {ip}\033[0m")
        except:
            pass
            
        q.task_done()
        time.sleep(0.05)

def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026": return

    clear()
    print(rgb_text(get_logo(), 5))

    while True:
        flush_input()
        print("\n\033[1;36m[ OSINT DISCOVERY MODE ]\033[0m")
        print(" Teknik ini tidak menebak, tapi melihat 'Sejarah SSL'.")
        print(" Sangat efektif untuk menemukan subdomain tua yang lupa diproteksi.")
        
        target = input("\n Target Domain (0 back): ").strip()
        if target == "0": return
        if not target: continue

        print(f"\n\033[1;32m[+] TARGET: {target}\033[0m")
        
        start_time = time.time()
        subs = fetch_crt_sh(target)
        
        if not subs:
            print(" \033[1;31m[!] Tidak ditemukan history SSL atau target terlalu baru.\033[0m")
        else:
            print(f" \033[1;32m[+] Ditemukan {len(subs)} subdomain unik dari database!\033[0m")
            time.sleep(1)
            
            print(f"\033[1;33m[+] MEMERIKSA STATUS AKTIF...\033[0m")
            print("\033[1;30m--------------------------------------------------\033[0m")
            
            q = Queue()
            results = []
            print_lock = threading.Lock()
            
            for s in subs:
                q.put(s)
                
            for _ in range(20):
                t = threading.Thread(target=worker, args=(q, results, print_lock))
                t.daemon = True
                t.start()
                
            q.join()
            
            sys.stdout.write(f"\r\033[K")
            print("\033[1;30m--------------------------------------------------\033[0m")
            
            origins = [r for r in results if r[2] == "ORIGIN"]
            
            if origins:
                print(f"\n\033[1;31m 💀 [ REPORT: BUNKER LEAKED ]\033[0m")
                print(f" Ditemukan {len(origins)} IP ASLI yang terekspos.")
                print(" Cek subdomain tua atau dev yang lupa dipasang Cloudflare.")
            else:
                print(f"\n\033[1;32m 🛡️ [ REPORT: CLEAN ]\033[0m")
                print(" Semua subdomain historis yang aktif sudah terlindungi CDN.")

        while True:
            print("\n 1. Scan Another Target")
            print(" 2. Save Result")
            print(" 0. Back")
            choice = input(" Select: ").strip()
            
            if choice == "1": break
            if choice == "0": return
            if choice == "2" and 'results' in locals() and results:
                fname = f"osint_{target}.txt"
                with open(fname, "w") as f:
                    for url, ip, stat in results:
                        f.write(f"[{stat}] {url} -> {ip}\n")
                print(f"\033[1;32m[+] Saved: {fname}\033[0m")

if __name__ == "__main__":
    print("[!] Load from login.py only")
