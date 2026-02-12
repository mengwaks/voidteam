import os
import time
import sys

# --- KONFIGURASI PASSWORD ---
# Ganti "omeng123" dengan password yang kamu mau
PASSWORD_RAHASIA = "omengganteng"

def bersihkan_layar():
    os.system('clear')

def banner():
    print("\033[1;36m") # Warna Cyan
    print("========================================")
    print("       Where Logic Ends. The Void Begins        ")
    print("========================================")
    print("\033[0m")

def menu_utama():
    bersihkan_layar()
    print("\033[1;32m") # Warna Hijau
    print("========================================")
    print("      VOID TEAM TOOLS - INISIAL V      ")
    print("========================================")
    print("1. TOOLS")
    print("2. TOOLS")
    print("3. Keluar")
    print("========================================")
    # Di sini nanti bisa ditambah logika tools-nya
    pilihan = input("Pilih menu (1-3): ")
    if pilihan == '3':
        print("Bye bye!")
        sys.exit()
    else:
        print(f"Kamu memilih menu {pilihan}. (Fitur belum dibuat)")

def login():
    bersihkan_layar()
    banner()
    
    # Loop biar kalau salah bisa coba lagi 3x
    kesempatan = 3
    
    while kesempatan > 0:
        print(f"\033[1;33m[!] Masukkan Password untuk akses tools ini.")
        print(f"[!] Kesempatan: {kesempatan}x lagi\033[0m")
        
        # Input password
        try:
            password = input("Password: ")
        except KeyboardInterrupt:
            print("\nKeluar paksa...")
            sys.exit()

        if password == PASSWORD_RAHASIA:
            print("\n\033[1;32m[+] AKSES DITERIMA! Selamat datang Boss.\033[0m")
            time.sleep(2) # Jeda 2 detik biar keren
            menu_utama()
            break
        else:
            print("\n\033[1;31m[X] PASSWORD SALAH! Coba lagi.\033[0m\n")
            kesempatan -= 1
            
    if kesempatan == 0:
        print("\n\033[1;41m[!] ACCESS DECLINE : YOU ARE NOT PART OF VOID TEAM [!]\033[0m")
        sys.exit()

if __name__ == "__main__":
    login()
