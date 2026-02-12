import os
import time
import sys
import math
import void_scanner

PASSWORD_RAHASIA = "".join([chr(x) for x in [111, 109, 101, 110, 103, 103, 97, 110, 116, 101, 110, 103]])

def bersihkan_layar():
    os.system('clear')

def rgb_text(text, offset):
    colored_chars = []
    FREQ = 0.1
    for i, char in enumerate(text):
        if char == '\n':
            colored_chars.append('\n')
            continue
        r = int(math.sin(FREQ * i + offset) * 127 + 128)
        g = int(math.sin(FREQ * i + offset + 2) * 127 + 128)
        b = int(math.sin(FREQ * i + offset + 4) * 127 + 128)
        colored_chars.append(f"\033[38;2;{r};{g};{b}m{char}")
    return "".join(colored_chars) + "\033[0m"

def get_logo():
    return r"""
 ░▒▓██████▓▒░      ▄▄██████▄▄      ░▒▓██████▓▒░
 ░▒▓██▓▒░        ▄████████████▄        ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▀▄ ▓▓ ▄▀ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░       ███ ▓▓ ▼▼ ▓▓ ███       ░▒▓██▓▒░
 ░▒▓██▓▒░        ▀████████████▀        ░▒▓██▓▒░
  ░▒▓██▓▒░         ▀▀██████▀▀         ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║    V  O  I  D     T  E  A  M     ║
        ╚══════════════════════════════════╝
           [ 0xVOID-INISIAL-V-001 ]
    """

def intro_animasi():
    try:
        sys.stdout.write("\033[?25l")
        for i in range(100): 
            sys.stdout.write("\033[H")
            sys.stdout.write(rgb_text(get_logo(), i * 0.2)) 
            sys.stdout.flush()
            time.sleep(0.04)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h")

def menu_utama():
    while True:
        bersihkan_layar()
        print(rgb_text(get_logo(), 5)) 
        
        print("\n\033[1;32m [ MENU UTAMA - INISIAL V ]\033[0m")
        print("========================================")
        print(" 1. VOID-SCANNER")
        print(" 2. Null")
        print(" 3. Keluar")
        print("========================================")
        
        try:
            pilihan = input(" Pilih menu (1-3): ")
            
            if pilihan == '1':
                # Bagian ini sekarang sudah sejajar dan rapi
                void_scanner.run_scanner("VOID_ACCESS_GRANTED_2026")
            elif pilihan == '2':
                print("\n[!] Menjalankan Script...")
                time.sleep(2)
            elif pilihan == '3':
                print("\nGood Bye, Master!")
                sys.exit()
            else:
                print(f"\n[!] Menu {pilihan} tidak ada.")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nGood Bye, Master!")
            sys.exit()

def login():
    bersihkan_layar()
    print("\033[1;36m")
    print("========================================")
    print("    Where Logic Ends, The Void Begins   ")
    print("========================================")
    print("\033[0m")
    
    kesempatan = 3
    
    while kesempatan > 0:
        print(f"\033[1;33m[!] SECURITY CHECK: Masukkan Password.")
        print(f"[!] Kesempatan: {kesempatan}x lagi\033[0m")
        
        try:
            password = input("Password: ").strip()
        except KeyboardInterrupt:
            sys.exit()

        if not password:
            print("\n\033[1;31m[!] Password tidak boleh kosong!\033[0m\n")
            continue

        if password == PASSWORD_RAHASIA:
            print("\n\033[1;32m[+] AKSES DITERIMA! Selamat datang Boss.\033[0m")
            time.sleep(1)
            bersihkan_layar()
            intro_animasi()
            menu_utama()
            break
        else:
            print("\n\033[1;31m[X] PASSWORD SALAH! Coba lagi.\033[0m\n")
            kesempatan -= 1
            
    if kesempatan == 0:
        print("\n\033[1;41m[!] ACCESS DECLINED : YOU ARE NOT PART OF VOID TEAM [!]\033[0m")
        sys.exit()

if __name__ == "__main__":
    login()
