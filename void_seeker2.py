import socket
import os
import sys
import time
import math
import threading
import json
import ssl
import urllib.request
import re
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

def get_logo():
    return r"""
 ░▒▓██████▓▒░      ▄▄██████▄▄      ░▒▓██████▓▒░
 ░▒▓██▓▒░        ▄████████████▄        ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▀▄ ▓▓ ▄▀ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▓▓ ▼▼ ▓▓ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░        ▀████████████▀        ░▒▓██▓▒░
  ░▒▓██▓▒░         ▀▀██████▀▀         ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║     V O I D - S E E K E R  V7    ║
        ╚══════════════════════════════════╝
           [ GOD EYE: API + CONTENT VERIFY ]
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
# INTELLIGENCE DATABASE
# =========================
CDN_RANGES = [
    "104.", "172.64.", "172.65.", "172.66.", "172.67.", "108.162.", "162.15.", "190.93.", "198.41.", # Cloudflare
    "23.", "104.", "184.", "2.16.", "2.23.", "2.18.", "2.19.", "2.20.", "2.21.", "2.22.", # Akamai
    "34.", "35.", "104.154.", "104.196.", "35.190", # Google
    "13.", "151.101.", "199.232.", "3.", "18.", "52.", "54." # AWS/Fastly
]

def is_protected(ip):
    for prefix in CDN_RANGES:
        if ip.startswith(prefix):
            return True
    return False

# =========================
# BIG DATA ENGINE
# =========================
def get_title(ip, host):
    """Mencuri Judul Website dari IP langsung"""
    try:
        url = f"http://{ip}"
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0', 'Host': host} 
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        with urllib.request.urlopen(req, context=ctx, timeout=3) as response:
            content = response.read().decode('utf-8', errors='ignore')
            title = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            if title:
                return title.group(1).strip()
    except:
        pass
    return None

def fetch_omnisint(domain):
    print(f" \033[1;34m[*] Mengakses Database OmniSint (Big Data)...\033[0m")
    url = f"https://sonar.omnisint.io/subdomains/{domain}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode())
        return data 
    except:
        return []

def fetch_crt_sh(domain):
    print(f" \033[1;34m[*] Mengakses Database SSL History...\033[0m")
    subdomains = set()
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode())
        for entry in data:
            name_value = entry['name_value']
            for sub in name_value.split('\n'):
                if "*" not in sub and sub.endswith(domain):
                    subdomains.add(sub)
        return list(subdomains)
    except:
        return []

# =========================
# VERIFICATION WORKER
# =========================
def worker(q, results, print_lock, target_domain):
    while not q.empty():
        sub = q.get()
        
        with print_lock:
            sys.stdout.write(f"\r\033[K \033[1;30m[-] Analyzing: {sub[:40]}...\033[0m")
            sys.stdout.flush()
        
        try:
            ip = socket.gethostbyname(sub)
            
            if not is_protected(ip):
                title = get_title(ip, target_domain)
                
                with print_lock:
                    sys.stdout.write(f"\r\033[K")
                    if title:
                        print(f" \033[1;41m[BOOM] {sub} -> {ip}\033[0m")
                        print(f" \033[1;33m       Title: {title[:50]} (MATCHED)\033[0m")
                        results.append((sub, ip, "CONFIRMED"))
                    else:
                        print(f" \033[1;32m[OPEN] {sub} -> {ip} (Not CDN)\033[0m")
                        results.append((sub, ip, "POTENTIAL"))
        except:
            pass
            
        q.task_done()
        time.sleep(0.01)

# =========================
# MAIN MODULE
# =========================
def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026": return

    while True:
        clear()
        print(rgb_text(get_logo(), 5))

        print("\n\033[1;36m[ GOD EYE PROTOCOL ]\033[0m")
        print(" 1. Full Scan (API + Verification)")
        print(" 0. Back")
        
        flush_input() # FIX: Bersihkan sisa input sebelumnya
        choice = input("\n Select: ").strip()

        if choice == "0":
            return
            
        elif choice == "1":
            target = ""
            # FIX: Loop ini memastikan input domain tidak bisa diskip
            while not target:
                flush_input() 
                target = input("\n Target Domain (e.g. site.com): ").strip()
                if not target:
                    print(" \033[1;31m[!] Domain tidak boleh kosong!\033[0m")
            
            print(f"\n\033[1;32m[+] TARGET: {target}\033[0m")
            
            # --- START SCANNING ---
            subs_omni = fetch_omnisint(target)
            subs_crt = fetch_crt_sh(target)
            
            all_subs = set(subs_omni + subs_crt)
            
            # Manual List Wajib
            critical_list = ["direct", "ftp", "cpanel", "mail", "dev", "origin", "backend", "webmail", "smtp"]
            for c in critical_list:
                all_subs.add(f"{c}.{target}")
            
            total = list(all_subs)
            print(f" \033[1;36m[+] DATA COLLECTED: {len(total)} Unique Subdomains\033[0m")
            
            if len(total) == 0:
                print(" \033[1;31m[!] API Gagal / Target terlalu kecil. Coba lagi nanti.\033[0m")
                time.sleep(2)
                continue # Balik ke menu jika gagal

            print("\n\033[1;33m[+] STARTING VERIFICATION ENGINE...\033[0m")
            print("\033[1;30m--------------------------------------------------\033[0m")
            
            q = Queue()
            results = []
            print_lock = threading.Lock()
            
            for s in total:
                q.put(s)
                
            # Threads
            for _ in range(50):
                t = threading.Thread(target=worker, args=(q, results, print_lock, target))
                t.daemon = True
                t.start()
            
            q.join()
            
            # REPORT
            sys.stdout.write(f"\r\033[K")
            print("\033[1;30m--------------------------------------------------\033[0m")
            
            confirmed = [r for r in results if r[2] == "CONFIRMED"]
            potential = [r for r in results if r[2] == "POTENTIAL"]
            
            if confirmed:
                print(f"\n\033[1;31m 💀 [ JACKPOT: {len(confirmed)} REAL ORIGIN FOUND ]\033[0m")
                for sub, ip, _ in confirmed:
                     print(f" -> {ip} ({sub})")
            elif potential:
                print(f"\n\033[1;32m ⚠️ [ WARNING: {len(potential)} POTENTIAL LEAKS ]\033[0m")
                print(" IP ini bukan Cloudflare. Cek manual!")
                for sub, ip, _ in potential:
                     print(f" -> {ip} ({sub})")
            else:
                print(f"\n\033[1;30m [ SECURE ] Target ini benar-benar kuat (Full Proxy).\033[0m")

            # Pause agar hasil tidak hilang
            input("\n Tekan Enter untuk kembali...")

if __name__ == "__main__":
    print("[!] Load from login.py only")
