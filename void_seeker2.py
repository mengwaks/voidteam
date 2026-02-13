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
# KONFIGURASI TITAN
# =========================
THREADS = 50
TIMEOUT = 5
socket.setdefaulttimeout(TIMEOUT)

# IP CDN / PELINDUNG (Musuh Kita)
CDN_RANGES = [
    "104.", "172.64.", "172.65.", "172.66.", "172.67.", "108.162.", "162.15.", "190.93.", "198.41.", # Cloudflare
    "23.", "104.", "184.", "2.16.", "2.23.", "2.18.", "2.19.", "2.20.", "2.21.", "2.22.", # Akamai
    "34.", "35.", "104.154.", "104.196.", "35.190", # Google
    "13.", "151.101.", "199.232.", "3.", "18.", "52.", "54.", # AWS/Fastly
    "192.168.", "127.0.", "10." # Local
]

# SUBDOMAIN WAJIB TEMBUS (Brute Force)
CRITICAL_LIST = [
    "direct", "ftp", "cpanel", "whm", "webmail", "mail", "smtp", "pop", 
    "dev", "test", "stage", "origin", "backend", "server", "admin", 
    "root", "vps", "ssh", "panel", "beta", "m", "support", "billing", 
    "shop", "blog", "forum", "mysql", "db", "sql", "remote", "vpn"
]

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
        ║     V O I D - T I T A N  V9      ║
        ╚══════════════════════════════════╝
           [ ENGINE: GOD EYE + BYPASS ]
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
# LOGIC ENGINE
# =========================
def is_protected(ip):
    """Cek apakah IP milik Cloudflare/CDN"""
    for prefix in CDN_RANGES:
        if ip.startswith(prefix):
            return True
    return False

def get_title(ip, host):
    """Mencoba mengambil judul website dari IP langsung (Host Header Spoofing)"""
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

def fetch_data(domain):
    """Mengambil data dari berbagai sumber (API & SSL)"""
    subs = set()
    
    # 1. SSL History (CRT.SH)
    print(f" \033[1;34m[*] Phase 1: Hacking SSL History...\033[0m")
    try:
        url = f"https://crt.sh/?q=%.{domain}&output=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for entry in data:
                name_value = entry['name_value']
                for s in name_value.split('\n'):
                    if "*" not in s and s.endswith(domain):
                        subs.add(s)
    except:
        pass

    # 2. OmniSint API
    print(f" \033[1;34m[*] Phase 2: Querying Big Data...\033[0m")
    try:
        url = f"https://sonar.omnisint.io/subdomains/{domain}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            for s in data:
                subs.add(s)
    except:
        pass
        
    # 3. Inject Critical List
    print(f" \033[1;34m[*] Phase 3: Injecting {len(CRITICAL_LIST)} Backdoor Words...\033[0m")
    for word in CRITICAL_LIST:
        subs.add(f"{word}.{domain}")

    return list(subs)

# =========================
# THREAD WORKER
# =========================
def worker(q, results, print_lock, target_domain):
    while not q.empty():
        try:
            sub = q.get_nowait()
        except:
            break

        # Visual Update
        with print_lock:
            sys.stdout.write(f"\r\033[K \033[1;30m[-] Analyzing: {sub[:35]}...\033[0m")
            sys.stdout.flush()

        try:
            ip = socket.gethostbyname(sub)
            
            if not is_protected(ip):
                # IP BUKAN CDN! Cek Kontennya
                title = get_title(ip, target_domain)
                
                with print_lock:
                    sys.stdout.write(f"\r\033[K")
                    if title:
                        # KETEMU DAN KONTENNYA SAMA!
                        print(f" \033[1;41m[BOOM]\033[0m {sub} -> {ip}")
                        print(f" \033[1;33m       Title: {title[:40]}\033[0m")
                        results.append((sub, ip, "CONFIRMED"))
                    else:
                        # KETEMU TAPI KONTEN BEDA/KOSONG
                        print(f" \033[1;32m[OPEN]\033[0m {sub} -> {ip} (Raw IP)")
                        results.append((sub, ip, "POTENTIAL"))
        except:
            pass
        
        q.task_done()
        time.sleep(0.01)

# =========================
# SCAN ROUTINE
# =========================
def start_scan():
    clear()
    print(rgb_text(get_logo(), 5))
    
    # === INPUT LOCK SYSTEM (ANTI MENTAL) ===
    target = ""
    while not target:
        flush_input()
        try:
            raw_in = input("\n \033[1;33m[?] Target Domain (e.g., site.com): \033[0m").strip()
            if raw_in:
                target = raw_in
            else:
                print(" \033[1;31m[!] Domain cannot be empty!\033[0m")
        except KeyboardInterrupt:
            return # Ijinkan keluar hanya jika CTRL+C
    
    print(f"\n\033[1;32m [+] TARGET LOCKED: {target}\033[0m")
    
    # 1. GET DATA
    targets = fetch_data(target)
    print(f" \033[1;36m[+] TOTAL TARGETS: {len(targets)} Subdomains\033[0m")
    
    if not targets:
        print(" \033[1;31m[!] Failed to fetch data. Try manual scan later.\033[0m")
        input("\n Press Enter...")
        return

    # 2. PREPARE WAR
    print("\n\033[1;33m [+] LAUNCHING GOD EYE ENGINE...\033[0m")
    print("\033[1;30m" + "="*40 + "\033[0m")
    
    q = Queue()
    results = []
    print_lock = threading.Lock()
    
    for s in targets:
        q.put(s)
        
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(q, results, print_lock, target))
        t.daemon = True
        t.start()
        threads.append(t)
        
    # Wait for completion
    q.join()
    
    # 3. FINAL REPORT
    sys.stdout.write(f"\r\033[K")
    print("\033[1;30m" + "="*40 + "\033[0m")
    
    confirmed = [x for x in results if x[2] == "CONFIRMED"]
    potential = [x for x in results if x[2] == "POTENTIAL"]
    
    if confirmed:
        print(f"\n\033[1;41m 💀 JACKPOT: {len(confirmed)} REAL ORIGIN FOUND \033[0m")
        for sub, ip, _ in confirmed:
            print(f" -> {ip} ({sub})")
    elif potential:
        print(f"\n\033[1;32m ⚠️ WARNING: {len(potential)} POTENTIAL LEAKS \033[0m")
        for sub, ip, _ in potential:
            print(f" -> {ip} ({sub})")
    else:
        print(f"\n\033[1;30m [SECURE] Target is heavily protected (Full Cloudflare).\033[0m")

    print("\n\033[1;37m [ Press Enter to return to menu ] \033[0m")
    flush_input()
    input()

# =========================
# MAIN MENU HOOK
# =========================
def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026": return
    
    while True:
        clear()
        print(rgb_text(get_logo(), 5))
        print("\n\033[1;36m [ TITAN MENU ]\033[0m")
        print(" 1. Start God Eye Scan")
        print(" 0. Back to Main Menu")
        
        flush_input()
        choice = input("\n Select: ").strip()
        
        if choice == "1":
            start_scan() # Panggil fungsi scan yang terisolasi
        elif choice == "0":
            return
        else:
            continue

if __name__ == "__main__":
    print("[!] Run from login.py")
