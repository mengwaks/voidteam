import socket
import os
import time
import sys

def run_scanner(key):
    if key != "VOID_ACCESS_GRANTED_2026":
        print("\033[1;31m[!] ILLEGAL ACCESS DETECTED!")
        print("[!] Please run from login.py\033[0m")
        sys.exit()

    os.system('clear')
    print("\033[1;36m [ MODULE: VOID-SCANNER ACTIVATED ]\033[0m")
    print("\033[1;30m ==================================\033[0m")
    
    try:
        target = input("\n\033[1;33m [?] Masukkan Domain Target: \033[1;37m")
        if not target: return

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
            
    except Exception as e:
        print(f"\033[1;31m [!] Error: {e}\033[0m")
    
    input("\n\033[1;37m [✓] Selesai. Tekan Enter untuk kembali...\033[0m")

if __name__ == "__main__":
    print("\033[1;31m[!] ERROR: This module must be loaded from login.py\033[0m")
