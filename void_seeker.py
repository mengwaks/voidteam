import socket
import os
import sys
import time
import math

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
        ║       V O I D - S E E K E R      ║
        ╚══════════════════════════════════╝
           [ VERSION 2.5 : STABLE CORE ]
    """

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def flush_input():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        pass

SUBDOMAINS = [
    "direct", "direct-connect", "mail", "ftp", "cpanel", "whm", 
    "webmail", "dev", "test", "staging", "mysql", "sql", "api", 
    "admin", "portal", "server", "vpn", "m", "mobile", "backend",
    "beta", "secure", "store", "shop", "blog", "forum", "support",
    "ns1", "ns2", "smtp", "pop", "imap", "remote", "gateway"
]

def is_cloudflare(ip):
    # Cek Prefix Cloudflare
    cf_prefixes = ["104.", "172.", "108.", "162.", "190.", "197.", "198."]
    for prefix in cf_prefixes:
        if ip.startswith(prefix):
            return True
    return False

def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026":
        print("\033[1;31m[!] ILLEGAL ACCESS\033[0m")
        return

    clear()
    print(rgb_text(get_logo(), 5))

    while True:
        flush_input()
        print("\n\033[1;36m[ IP ORIGIN FINDER ]\033[0m")
        print(" This tool will brute-force subdomains to find Real IP.")
        
        target = input("\n Target Domain (0 back): ").strip()

        if target == "0":
            return
        if not target:
            continue

        print(f"\n\033[1;32m[+] TARGET : {target}\033[0m")
        print("\033[1;33m[+] SCANNING SUBDOMAINS...\033[0m")
        
        leaks = []
        start_time = time.time()

        try:
            for sub in SUBDOMAINS:
                full_url = f"{sub}.{target}"
                
                sys.stdout.write(f"\r\033[K \033[1;30m[-] Checking: {full_url}\033[0m")
                sys.stdout.flush()
                time.sleep(0.05) 

                try:
                    socket.setdefaulttimeout(1)
                    ip = socket.gethostbyname(full_url)
                    
                    if not is_cloudflare(ip):
                        sys.stdout.write(f"\r\033[K") 
                        print(f" \033[1;31m[!] FOUND: {full_url.ljust(25)} -> {ip}\033[0m")
                        leaks.append((full_url, ip))
                    else:
                        pass
                except:
                    pass
        
        except KeyboardInterrupt:
            print("\n\033[1;31m[!] Scan Interrupted\033[0m")
        
        sys.stdout.write(f"\r\033[K") 
        print(f"\033[1;30m----------------------------------------\033[0m")

        if leaks:
            print(f"\n\033[1;31m 💀 [ KESIMPULAN: BUNKER JEBOL ]\033[0m")
            print(f" Ditemukan {len(leaks)} kebocoran IP asli.")
        else:
            print(f"\n\033[1;32m 🛡️ [ KESIMPULAN: BUNKER SOLID ]\033[0m")
            print(f" Tidak ditemukan IP asli.")

        while True:
            print("\n 1. Scan another target")
            print(" 0. Back")

            choice = input("\n Select: ").strip()

            if choice == "1":
                break 
            
            elif choice == "0":
                return 
            
if __name__ == "__main__":
    print("[!] Load from login.py only")
