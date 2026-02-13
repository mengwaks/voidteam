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
           [ VERSION 2.5 : STABLE VISUAL ]
    """

SUBDOMAINS = [
    "direct", "direct-connect", "mail", "ftp", "cpanel", "whm", 
    "webmail", "dev", "test", "staging", "mysql", "sql", "api", 
    "admin", "portal", "server", "vpn", "m", "mobile", "backend",
    "beta", "secure", "store", "shop", "blog", "forum", "support",
    "ns1", "ns2", "smtp", "pop", "imap", "remote", "gateway"
]

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def is_cloudflare(ip):
    cf_prefixes = ["104.", "172.64.", "172.65.", "172.66.", "172.67.", "108.", "162.15", "190.", "197.", "198.41"]
    for prefix in cf_prefixes:
        if ip.startswith(prefix):
            return True
    return False

def seek_origin(target):
    print(f"\n\033[1;36m [*] Scanning Target: {target}\033[0m")
    print(f"\033[1;30m --------------------------------------------------\033[0m")
    
    leaks = []
    
    try:
        for sub in SUBDOMAINS:
            full_url = f"{sub}.{target}"
            
            sys.stdout.write(f"\r\033[K \033[1;30m[-] Checking: {full_url}\033[0m")
            sys.stdout.flush()
            
            time.sleep(0.05) 
            
            try:
                socket.setdefaulttimeout(2) 
                ip = socket.gethostbyname(full_url)
                
                if not is_cloudflare(ip):
                    sys.stdout.write(f"\r\033[K") 
                    print(f" \033[1;31m[!] ALERT: {full_url.ljust(25)} -> {ip} [ORIGIN!]\033[0m")
                    leaks.append((full_url, ip))
                else:
                    pass
            except:
                pass
                
    except KeyboardInterrupt:
        print("\n\n\033[1;33m [!] Scan interrupted by user.\033[0m")
    
    sys.stdout.write(f"\r\033[K")
    print(f"\033[1;30m --------------------------------------------------\033[0m")
    
    if leaks:
        print(f"\n\033[1;31m 💀 [ KESIMPULAN: BUNKER JEBOL ]\033[0m")
        print(f" Ditemukan {len(leaks)} titik kebocoran IP asli.")
    else:
        print(f"\n\033[1;32m 🛡️ [ KESIMPULAN: BUNKER SOLID ]\033[0m")
        print(f" Tidak ditemukan IP asli di list umum.")

def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026": return

    while True:
        clear()
        print(get_logo())
        
        print("\n\033[1;33m [?] Masukkan Domain Target (tanpa http/https)\033[0m")
        print(" \033[1;30m(Ketik '0' untuk kembali ke Menu Utama)\033[0m")
        
        target = input("\n root@void-seeker:~$ ").strip()
        
        if target == '0':
            return 
        
        if not target:
            continue
            
        seek_origin(target)
        
        print("\n\033[1;37m [ Tekan Enter untuk Scan Target Lain ]\033[0m")
        print("\033[1;30m [ Ketik '0' untuk Kembali ke Menu Utama ]\033[0m")
        
        choice = input(" Select: ").strip()
        
        if choice == '0':
            return
        

if __name__ == "__main__":
    run_seeker("VOID_ACCESS_GRANTED_2026")
