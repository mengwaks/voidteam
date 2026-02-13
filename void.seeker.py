import socket
import os
import sys
import time

def get_logo():
    return r"""
 ░▒▓██████▓▒░      ▄▄██████▄▄      ░▒▓██████▓▒░
 ░▒▓██▓▒░        ▄████████████▄        ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▀▄ ▓▓ ▄▀ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▓▓ ▼▼ ▓▓ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░        ▀████████████▀        ░▒▓██▓▒░
  ░▒▓██▓▒░         ▀▀██████▀▀         ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║       V O I D - S E E K E R      ║
        ╚══════════════════════════════════╝
           [ VERSION 2: SMART ANALYSIS ]
    """

SUBDOMAINS = [
    "direct", "direct-connect", "mail", "ftp", "cpanel", "whm", 
    "webmail", "dev", "test", "staging", "mysql", "sql", "api", 
    "admin", "portal", "server", "vpn", "m", "mobile", "backend"
]

def is_cloudflare(ip):
    cf_prefixes = ["104.", "172.", "108.", "162.", "190.", "197.", "198."]
    for prefix in cf_prefixes:
        if ip.startswith(prefix):
            return True
    return False

def seek_origin(target):
    print(f"\n\033[1;36m [*] Scanning Target: {target}\033[0m")
    print(f"\033[1;30m --------------------------------------------------\033[0m")
    
    leaks = []
    
    for sub in SUBDOMAINS:
        full_url = f"{sub}.{target}"
        sys.stdout.write(f"\r \033[1;30m[-] Checking: {full_url}...")
        sys.stdout.flush()
        
        try:
            ip = socket.gethostbyname(full_url)
            
            if not is_cloudflare(ip):
                print(f"\r \033[1;31m[!] ALERT: {full_url.ljust(25)} -> {ip} [ORIGIN FOUND!]\033[0m")
                leaks.append((full_url, ip))
            else:
                pass
        except:
            pass
            
    print(f"\033[1;30m\r --------------------------------------------------\033[0m")
    
    if leaks:
        print(f"\n\033[1;31m 💀 [ KESIMPULAN: BUNKER JEBOL ]\033[0m")
        print(f" Ditemukan {len(leaks)} titik kebocoran IP asli.")
        print(f" Black Hat bisa menyerang IP ini langsung dan mem-bypass Cloudflare.")
        for url, ip in leaks:
            print(f"  -> {url} ({ip})")
    else:
        print(f"\n\033[1;32m 🛡️ [ KESIMPULAN: BUNKER SOLID ]\033[0m")
        print(f" Tidak ditemukan IP asli melalui metode Subdomain Scrape.")
        print(f" Bunker kamu sementara aman dari pengintaian dasar.")

def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026": return
    os.system('clear')
    print(get_logo())
    domain = input("\n [?] Masukkan Domain Target: ").strip()
    if domain:
        seek_origin(domain)
        input("\n Tekan Enter untuk kembali...")
