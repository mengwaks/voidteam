import os
import time
import sys
import math

# --- KONFIGURASI PASSWORD (OBFUSCATED) ---
PASSWORD_RAHASIA = "".join([chr(x) for x in [111, 109, 101, 110, 103, 103, 97, 110, 116, 101, 110, 103]])

# --- FUNGSI WARNA & GAMBAR (BAGIAN MEWAH) ---
def rgb_text(text, offset):
    """Membuat teks menjadi warna-warni RGB bergerak"""
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
    """Logo Burung Hantu VOID TEAM"""
    return r"""
 ░▒▓██████▓▒░         ▄▄██████▄▄         ░▒▓██████▓▒░
 ░▒▓██▓▒░           ▄████████████▄           ░▒▓██▓▒░
 ░▒▓██▓▒░          ███ ▀▄ ▓▓ ▄▀ ███          ░▒▓██▓▒░
 ░▒▓██▓▒░          ███ ▓▓ ▼▼ ▓▓ ███          ░▒▓██▓▒░
 ░▒▓██▓▒░           ▀████████████▀           ░▒▓██▓▒░
  ░▒▓██▓▒░            ▀▀██████▀▀            ░▒▓██▓▒░
 
        ╔══════════════════════════════════╗
        ║    V  O  I  D     T  E  A  M     ║
        ╚══════════════════════════════════╝
           [ NFT HASH: 0xVOID-ALPHA-001 ]
    """

def intro_animasi():
    """Memutar animasi RGB selama 3 detik sebelum masuk menu"""
    try:
        sys.stdout.write("\033[?25l") # Sembunyikan kursor
        for i in range(40): # Jalan sekitar 2-3 detik
            sys.stdout.write("\033[H") # Kursor ke atas (biar gak kedip)
            # Render logo dengan warna berjalan (offset i * 0.2)
            sys.stdout.write(rgb_text(get_logo(), i * 0.2)) 
            sys.stdout.flush()
            time.sleep(0.05)
    except:
        pass
    finally:
        sys.stdout.write("\033[?25h") # Munculkan kursor lagi

# --- FUNGSI UTAMA ---

def bersihkan_layar():
    os.system('clear')

def banner_login():
    # Banner simpel khusus untuk halaman login
    print("\033[1;36m")
    print("========================================")
    print("    Where Logic Ends, The Void Begins   ")
    print("========================================")
    print("\033[0m")

def menu_utama():
    bersihkan_layar()
    
    # Tampilkan Logo VOID TEAM (Static tapi berwarna RGB mewah)
    print(rgb_text(get_logo(), 5)) 
    
    print("\n\033[1;32m [ MENU UTAMA - INISIAL V ]\033[0m")
    print("========================================")
    print(" 1. Install Bahan")
    print(" 2. Jalankan Script Hack")
    print(" 3. Keluar")
    print("========================================")
    
    pilihan = input(" Pilih menu (1-3): ")
    if pilihan == '3':
        print("\nGood Bye, Master!")
        sys.exit()
    else:
        print(f"\n[!] Kamu memilih menu {pilihan}. (Fitur ini belum dibuat)")
        time.sleep(2)
        menu_utama() # Kembali ke menu

def login():
    bersihkan_layar()
    banner_login()
    
    kesempatan = 3
    
    while kesempatan > 0:
        print(f"\033[1;33m[!] SECURITY CHECK: Masukkan Password.")
        print(f"[!] Kesempatan: {kesempatan}x lagi\033[0m")
        
        try:
            password = input("Password: ")
        except KeyboardInterrupt:
            print("\nKeluar paksa...")
            sys.exit()

        if password == PASSWORD_RAHASIA:
            print("\n\033[1;32m[+] AKSES DITERIMA! Selamat datang Boss.\033[0m")
            time.sleep(1)
            
            # --- INI BAGIAN YANG DITAMBAHKAN ---
            bersihkan_layar()
            intro_animasi() # Memutar animasi burung hantu RGB
            # -----------------------------------
            
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
