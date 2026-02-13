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
        ║     V O I D - S E E K E R  V4    ║
        ╚══════════════════════════════════╝
           [ HYBRID: OSINT + BYPASS ATTACK ]
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
# DATA & WORDLIST
# =========================
CDN_RANGES = {
    "CLOUDFLARE": ["104.", "172.64.", "172.65.", "172.66.", "172.67.", "108.162.", "162.15.", "190.93.", "198.41."],
    "AKAMAI": ["23.", "104.", "184.", "2.16.", "2.23."],
    "GOOGLE": ["34.", "35.", "104.154.", "104.196."],
    "AWS": ["3.", "13.", "18.", "52.", "54."]
}

# Subdomain yang sering LUPA dipasang Cloudflare (Direct IP)
BYPASS_LIST = [
    "direct", "direct-connect", "ftp", "cpanel", "whm", "webmail",
    "mail", "email", "smtp", "pop", "pop3", "imap",
    "dev", "development", "test", "testing", "stage", "staging", "uat",
    "admin", "administrator", "backend", "panel", "control",
    "server", "server1", "vps", "root", "origin", "source",
    "db", "mysql", "sql", "database", "phpmyadmin",
    "api", "api-dev", "beta", "support", "billing", "portal",
    "blog", "forum", "shop", "store", "m", "mobile",
    "ns1", "ns2", "dns1", "dns2", "remote", "vpn", "gateway"
]

def get_provider_status(ip):
    for provider, prefixes in CDN_RANGES.items():
        for prefix in prefixes:
            if ip.startswith(prefix):
                return provider
    return "ORIGIN"

# =========================
# LOGIC ENGINES
# =========================
def fetch_crt_sh(domain):
    """Phase 1: OSINT"""
    print(f" \033[1;34m[*] PHASE 1: Checking SSL History (OSINT)...\033[0m")
    subdomains = set()
    url = f"https://crt.sh/?q=%.{domain}&output=json"
    
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = json.loads(response.read().decode())
            
        for entry in data:
            name_value = entry['name_value']
            for sub in name_value.split('\n'):
                if "*" not in sub and sub.endswith(domain):
                    subdomains.add(sub)
        return list(subdomains)
    except:
        return []

def worker(q, results, print_lock):
    while not q.empty():
        full_url = q.get()
        
        with print_lock:
            # Overwrite line visual
            sys.stdout.write(f"\r\033[K \033[1;30m[-] Scanning: {full_url[:40]}...\033[0m")
            sys.stdout.flush()
        
        try:
            ip = socket.gethostbyname(full_url)
            status = get_provider_status(ip)
            
            with print_lock:
                if status == "ORIGIN":
                    # KETEMU IP ASLI
                    sys.stdout.write(f"\r\033[K")
                    print(f" \033[1;32m[ORIGIN] {full_url.ljust(35)} -> {ip}\033[0m")
                    results.append((full_url, ip, "ORIGIN"))
                else:
                    # KETEMU CDN (Disimpan tapi tidak di-highlight)
                    results.append((full_url, ip, status))
        except:
            pass
            
        q.task_done()
        time.sleep(0.02)

# =========================
# MAIN MODULE
# =========================
def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026": return

    while True:
        clear()
        print(rgb_text(get_logo(), 5))

        print("\n\033[1;36m[ HYBRID SEEKER PROTOCOL ]\033[0m")
        print(" 1. Auto-Scan (OSINT + Brute Force Fallback)")
        print(" 0. Back")
        
        # PERBAIKAN LOGIKA INPUT AGAR TIDAK LEWAT
        try:
            choice = input("\n Select: ").strip()
        except EOFError:
            continue

        if choice == "0": 
            return # Kembali ke menu utama

        elif choice == "1":
            # LOGIKA PENGUNCIAN: Paksa user input target, jangan balik ke menu
            target = ""
            while not target:
                try:
                    target = input("\n Target Domain (e.g. site.com): ").strip()
                    if not target:
                        print(" \033[1;31m[!] Domain tidak boleh kosong!\033[0m")
                except KeyboardInterrupt:
                    return # Ijinkan keluar jika CTRL+C

            print(f"\n\033[1;32m[+] TARGET: {target}\033[0m")
            
            # --- PHASE 1: OSINT ---
            osint_subs = fetch_crt_sh(target)
            unique_targets = set(osint_subs)
            
            print(f" \033[1;32m[+] OSINT Result: {len(osint_subs)} subdomains found.\033[0m")
            
            # --- PHASE 2: ADDING BYPASS LIST ---
            print(f" \033[1;34m[*] PHASE 2: Injecting 'Bypass List' (Common Leaks)...\033[0m")
            for word in BYPASS_LIST:
                unique_targets.add(f"{word}.{target}")
                
            total_targets = list(unique_targets)
            print(f" \033[1;36m[+] TOTAL TARGETS TO SCAN: {len(total_targets)}\033[0m")
            time.sleep(1)
            
            # --- PHASE 3: EXECUTION ---
            print("\n\033[1;33m[+] EXECUTING SCAN...\033[0m")
            print("\033[1;30m--------------------------------------------------\033[0m")
            
            q = Queue()
            results = []
            print_lock = threading.Lock()
            
            for sub in total_targets:
                q.put(sub)
                
            # 30 Threads
            for _ in range(30):
                t = threading.Thread(target=worker, args=(q, results, print_lock))
                t.daemon = True
                t.start()
                
            q.join()
            
            # --- REPORT ---
            sys.stdout.write(f"\r\033[K")
            print("\033[1;30m--------------------------------------------------\033[0m")
            
            origins = [r for r in results if r[2] == "ORIGIN"]
            
            if origins:
                print(f"\n\033[1;31m 💀 [ REPORT: BUNKER LEAKED ]\033[0m")
                print(f" Ditemukan {len(origins)} IP ASLI (ORIGIN).")
            else:
                print(f"\n\033[1;32m 🛡️ [ REPORT: SECURE ]\033[0m")
                print(" Semua subdomain yang dicek (OSINT + Common) terlindungi.")

            # HOLD SCREEN (Biar hasil gak hilang)
            while True:
                print("\n 1. Scan Another Target")
                print(" 2. Save Result")
                print(" 0. Back")
                sel = input(" Select: ").strip()
                
                if sel == "1": break # Break loop hold, balik ke loop menu (tapi karena logic, dia akan clear screen)
                if sel == "0": return # Balik ke login.py
                if sel == "2" and results:
                    fname = f"hybrid_{target}.txt"
                    with open(fname, "w") as f:
                        for url, ip, stat in results:
                            f.write(f"[{stat}] {url} -> {ip}\n")
                    print(f"\033[1;32m[+] Saved: {fname}\033[0m")

        else:
            # Jika input ngaco (bukan 0 atau 1)
            continue

if __name__ == "__main__":
    print("[!] Load from login.py only")
