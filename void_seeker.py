import socket
import os
import sys
import time
import math
import threading
import random
import ipaddress
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
        ║       V O I D - M A P P E R      ║
        ╚══════════════════════════════════╝
           [ INFRASTRUCTURE & IP REVEALER ]
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
    "FASTLY": ["151.101.", "199.232."],
    "GOOGLE": ["34.", "35.", "104.154.", "104.196."],
    "AMAZON_AWS": ["3.", "13.", "18.", "52.", "54."],
    "MICROSOFT": ["13.", "20.", "40.", "52."]
}

BASE_WORDS = [
    "www", "mail", "remote", "blog", "webmail", "server", "ns1", "ns2", 
    "test", "dev", "shop", "api", "vpn", "secure", "ftp", "cpanel", "whm", 
    "direct", "portal", "admin", "backend", "db", "mysql", "staging", "beta",
    "support", "billing", "status", "mobile", "m", "en", "id", "account"
]

CONNECTORS = [".", "-"]
SUFFIXES = ["01", "1", "2", "new", "old", "bak"]

def get_provider(ip):
    """Mendeteksi siapa pemilik IP tersebut"""
    for provider, prefixes in CDN_RANGES.items():
        for prefix in prefixes:
            if ip.startswith(prefix):
                return f"\033[1;33m[{provider}]\033[0m" 
    
    return f"\033[1;31m[ORIGIN/UNKNOWN]\033[0m" 

def generate_mutations():
    """Generator Subdomain Tanpa Henti"""
    for w in BASE_WORDS: yield w
    
    for w in BASE_WORDS:
        for i in range(1, 10): yield f"{w}{i}"
        for i in range(1, 10): yield f"{w}0{i}"

    for w in BASE_WORDS:
        for c in CONNECTORS:
            for s in SUFFIXES:
                yield f"{w}{c}{s}"
    
    while True:
        w1 = random.choice(BASE_WORDS)
        w2 = random.choice(BASE_WORDS)
        yield f"{w1}-{w2}"

def check_target(target, full_url, print_lock, seen_ips):
    try:
        ip = socket.gethostbyname(full_url)
        
        provider_label = get_provider(ip)
        
        with print_lock:
            sys.stdout.write(f"\r\033[K")
            
            if "ORIGIN" in provider_label:
                 print(f" {provider_label} {full_url.ljust(30)} -> {ip}")
            else:
                 print(f" {provider_label} {full_url.ljust(30)} -> {ip}")
                 
    except:
        pass 
def worker(q, target, stop_event, print_lock, seen_ips):
    while not stop_event.is_set():
        sub = q.get()
        full_url = f"{sub}.{target}"
        
        with print_lock:
            sys.stdout.write(f"\r\033[K \033[1;36m[∞] MAPPING: {full_url} ...\033[0m")
            sys.stdout.flush()
            
        check_target(target, full_url, print_lock, seen_ips)
        q.task_done()
        time.sleep(0.01)

def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026": return

    clear()
    print(rgb_text(get_logo(), 5))

    while True:
        flush_input()
        print("\n\033[1;36m[ NETWORK MAPPER ]\033[0m")
        print(" Bot akan menampilkan SEMUA IP dan PROVIDER-nya.")
        print(" Biarkan berjalan untuk melihat lompatan CDN.")
        
        target = input("\n Target Domain (0 back): ").strip()
        if target == "0": return
        if not target: continue

        print(f"\n\033[1;32m[+] TARGET: {target}\033[0m")
        print("\033[1;30m--------------------------------------------------\033[0m")
        print(f" TYPE             DOMAIN                         IP ADDRESS")
        print("\033[1;30m--------------------------------------------------\033[0m")
        
        q = Queue()
        stop_event = threading.Event()
        print_lock = threading.Lock()
        seen_ips = set() 
        
        for _ in range(15):
            t = threading.Thread(target=worker, args=(q, target, stop_event, print_lock, seen_ips))
            t.daemon = True
            t.start()

        gen = generate_mutations()
        
        try:
            while True:
                if q.qsize() < 50:
                    q.put(next(gen))
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            stop_event.set()
            print("\n\n\033[1;31m[!] MAPPING STOPPED.\033[0m")
        
        while True:
            print("\n 1. Map Another Target")
            print(" 0. Back")
            choice = input(" Select: ").strip()
            if choice == "1": break
            if choice == "0": return

if __name__ == "__main__":
    print("[!] Load from login.py only")
