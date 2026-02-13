import os
import time
import sys
import math

# --- IMPORT MODULES ---
try:
    import void_scanner
except ImportError:
    void_scanner = None

try:
    import void_seeker
except ImportError:
    void_seeker = None

try:
    import void_seeker2
except ImportError:
    void_seeker2 = None

try:
    import void_ddos
except ImportError:
    void_ddos = None

try:
    import void_bypass
except ImportError:
    void_bypass = None


# --- PASSWORD ---
PASSWORD_RAHASIA = "".join(
    chr(x) for x in [111, 109, 101, 110, 103, 103, 97, 110, 116, 101, 110, 103]
)

# --- UTILS ---
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def flush_input():
    try:
        import termios
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except:
        pass

def rgb_text(text, offset=0):
    FREQ = 0.1
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
        ║      V O I D   T E A M           ║
        ╚══════════════════════════════════╝
                  [ LOGIN CORE ]
    """

def intro_animation():
    try:
        sys.stdout.write("\033[?25l")
        for i in range(101):
            sys.stdout.write("\033[2J\033[H")
            print(rgb_text(get_logo(), i * 0.2))
            print(rgb_text(f"\n   [ BOOTING SYSTEM {i}% ]", i * 0.2))
            sys.stdout.flush()
            time.sleep(0.035)
    finally:
        sys.stdout.write("\033[?25h\033[0m")

# --- MENU UTAMA ---
def menu_utama():
    while True:
        clear_screen()
        print(rgb_text(get_logo(), 5))

        print("\n\033[1;32m[ MAIN MENU ]\033[0m")
        print("\033[1;30m========================================\033[0m")
        print(" 1. VOID-SCANNER (LEVEL C / X MAX)")
        print(" 2. VOID-SEEKER  (IP ORIGIN FINDER)")
        print(" 3. VOID-SEEKER2 (TITAN ENGINE V9)")
        print(" 4. VOID-DDoS    (BUNKER STRESSER)")
        print(" 5. VOID-BYPASS  (DIRECT ORIGIN STRESSER)")
        print(" 0. Exit")
        print("\033[1;30m========================================\033[0m")

        flush_input()
        choice = input(" Select: ").strip()

        if choice == "1":
            if void_scanner is None:
                print("\n\033[1;31m[!] void_scanner.py not found\033[0m")
                time.sleep(2)
                continue
            flush_input()
            time.sleep(0.2)
            void_scanner.run_scanner("VOID_ACCESS_GRANTED_2026")

        elif choice == "2":
            if void_seeker is None:
                print("\n\033[1;31m[!] void_seeker.py not found\033[0m")
                time.sleep(2)
                continue
            flush_input()
            time.sleep(0.2)
            void_seeker.run_seeker("VOID_ACCESS_GRANTED_2026")

        elif choice == "3":
            if void_seeker2 is None:
                print("\n\033[1;31m[!] void_seeker2.py not found\033[0m")
                time.sleep(2)
                continue
            flush_input()
            time.sleep(0.2)
            void_seeker2.run_seeker("VOID_ACCESS_GRANTED_2026")

        elif choice == "4":
            if void_ddos is None:
                print("\n\033[1;31m[!] void_ddos.py not found\033[0m")
                time.sleep(2)
                continue
            flush_input()
            time.sleep(0.2)
            void_ddos.run_ddos("VOID_ACCESS_GRANTED_2026")

        elif choice == "5":
            if void_bypass is None:
                print("\n\033[1;31m[!] void_bypass.py not found\033[0m")
                time.sleep(2)
                continue
            flush_input()
            time.sleep(0.2)
            void_bypass.run_bypass("VOID_ACCESS_GRANTED_2026")

        elif choice == "0":
            print("\n\033[1;31mSession terminated.\033[0m")
            sys.exit()

        else:
            continue

# --- LOGIN ---
def login():
    clear_screen()
    print("\033[1;36m")
    print("========================================")
    print("    WHERE LOGIC ENDS, THE VOID BEGINS    ")
    print("========================================")
    print("\033[0m")

    attempts = 3

    while attempts > 0:
        print(f"\033[1;33m[ SECURITY CHECK ] Attempts left: {attempts}\033[0m")
        try:
            password = input(" Password: ").strip()
        except KeyboardInterrupt:
            sys.exit()

        if not password:
            print("\033[1;31m[!] Empty password denied\033[0m\n")
            continue

        if password == PASSWORD_RAHASIA:
            print("\n\033[1;32m[ ACCESS GRANTED ] Welcome back, Boss.\033[0m")
            time.sleep(1)
            intro_animation()
            menu_utama()
            return
        else:
            print("\033[1;31m[ ACCESS DENIED ] Wrong password\n\033[0m")
            attempts -= 1

    print("\033[1;41m[ VOID REJECTED YOU ] SESSION LOCKED\033[0m")
    sys.exit()


if __name__ == "__main__":
    login()
