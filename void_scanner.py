import socket
import os
import time
import sys

def run_scanner(key):
    # 1. Verifikasi Kunci Akses
    if key != "VOID_ACCESS_GRANTED_2026":
        print("\033[1;31m[!] ILLEGAL ACCESS DETECTED!")
        print("[!] Please run from login.py\033[0m")
        time.sleep(2)
        return # Gunakan return agar tidak menutup seluruh aplikasi

    os.system('clear')
    print("\033[1;36m [ MODULE: VOID-SCANNER ACTIVATED ]\033[0m")
    print("\033[1;30m ==================================\033[0m")
    
    # Beri jeda 0.2 detik agar input buffer bersih
    time.sleep(0.2)
    
    try:
        target = input("\n\033[1;33m [?] Masukkan Domain Target: \033[1;37m").strip()
        
        # Jika input kosong, jangan langsung return, tapi beri peringatan
        if not target:
            print("\n\033[1;31m [!] Error: Target tidak boleh kosong!\033[0m")
        else:
            print(f"\n\033[1;32m [+] Analyzing Target: {target}...\033[0m")
            ip_address = socket.gethostbyname(target)
            print(f"\033[1;36m [+] IP Address FOUND: {ip_address}\033[0m")

            ports = {21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS", 3306: "MySQL"}
            for port, service in ports.items():
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip_address, port))
                if result == 0:
                    print(f"     \033[1;32m[OPEN] Port {port} : {service}\033[0m")
                sock.close()
            
    except socket.gaierror:
        print(f"\n\033[1;31m [!] Error: Domain '{target}' tidak valid atau tidak ditemukan.\033[0m")
    except Exception as e:
        print(f"\n\033[1;31m [!] Error: {e}\033[0m")
    
    # PENTING: Penahan layar agar tidak langsung balik ke menu
    print("\n\033[1;30m ----------------------------------\033[0m")
    input("\033[1;37m [✓] Selesai. Tekan Enter untuk kembali ke Menu...\033[0m")

if __name__ == "__main__":
    print("\033[1;31m[!] ERROR: This module must be loaded from login.py\033[0m")
