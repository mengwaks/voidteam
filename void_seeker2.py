import socket
import os
import sys
import time
import math
import threading
import json
import ssl
import urllib.request
import re
from queue import Queue

# =========================
# GLOBAL CONFIG
# =========================
THREAD_COUNT = 50
SOCKET_TIMEOUT = 3

socket.setdefaulttimeout(SOCKET_TIMEOUT)

# =========================
# VISUAL ENGINE
# =========================
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
        ║     V O I D - S E E K E R  V8    ║
        ╚══════════════════════════════════╝
           [ GOD EYE: ORIGIN DISCOVERY ]
    """

def clear():
    os.system("cls" if os.name == "nt" else "clear")

# =========================
# CDN INTEL
# =========================
CDN_RANGES = (
    "104.", "172.64.", "172.65.", "172.66.", "172.67.",
    "108.162.", "162.15.", "190.93.", "198.41.",   # Cloudflare
    "23.", "184.", "2.16.", "2.18.", "2.19.", "2.20.", "2.21.", "2.22.",  # Akamai
    "34.", "35.", "104.154.", "104.196.", "35.190", # Google
    "13.", "151.101.", "199.232.", "3.", "18.", "52.", "54." # AWS/Fastly
)

def is_protected(ip: str) -> bool:
    return ip.startswith(CDN_RANGES)

# =========================
# DATA SOURCES
# =========================
def fetch_omnisint(domain):
    print("\033[1;34m[*] OmniSint lookup...\033[0m")
    try:
        with urllib.request.urlopen(
            f"https://sonar.omnisint.io/subdomains/{domain}",
            timeout=20
        ) as r:
            return json.loads(r.read().decode())
    except:
        return []

def fetch_crtsh(domain):
    print("\033[1;34m[*] crt.sh lookup...\033[0m")
    subs = set()
    try:
        with urllib.request.urlopen(
            f"https://crt.sh/?q=%.{domain}&output=json",
            timeout=20
        ) as r:
            data = json.loads(r.read().decode())
        for row in data:
            for s in row.get("name_value", "").splitlines():
                if "*" not in s and s.endswith(domain):
                    subs.add(s)
    except:
        pass
    return list(subs)

# =========================
# VERIFICATION
# =========================
def grab_title(ip, host):
    try:
        req = urllib.request.Request(
            f"http://{ip}",
            headers={"Host": host, "User-Agent": "Mozilla/5.0"}
        )
        ctx = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=ctx, timeout=SOCKET_TIMEOUT) as r:
            html = r.read().decode(errors="ignore")
        m = re.search(r"<title>(.*?)</title>", html, re.I)
        return m.group(1).strip() if m else None
    except:
        return None

# =========================
# WORKER ENGINE
# =========================
def worker(queue, results, lock, stats, target):
    while True:
        try:
            sub = queue.get_nowait()
        except:
            return

        try:
            ip = socket.gethostbyname(sub)
            if not is_protected(ip):
                title = grab_title(ip, target)
                with lock:
                    if title:
                        print(f"\033[1;41m[BOOM]\033[0m {sub} -> {ip}")
                        results.append(("CONFIRMED", sub, ip, title))
                    else:
                        print(f"\033[1;32m[OPEN]\033[0m {sub} -> {ip}")
                        results.append(("POTENTIAL", sub, ip, None))
        except:
            pass
        finally:
            with lock:
                stats["done"] += 1
            queue.task_done()

# =========================
# MAIN CORE
# =========================
def run_seeker(key):
    if key != "VOID_ACCESS_GRANTED_2026":
        return

    while True:
        clear()
        print(rgb_text(get_logo(), 5))
        print("\n\033[1;36m[ GOD EYE PROTOCOL ]\033[0m")
        print(" 1. Full Origin Scan")
        print(" 0. Exit")

        choice = input("\n Select: ").strip()
        if choice == "0":
            return
        if choice != "1":
            continue

        target = input("\n Target domain: ").strip()
        if not target:
            continue

        print(f"\n\033[1;32m[+] TARGET LOCKED: {target}\033[0m")

        subs = set(fetch_omnisint(target) + fetch_crtsh(target))
        for x in ("direct","ftp","cpanel","mail","dev","origin","backend","smtp"):
            subs.add(f"{x}.{target}")

        if not subs:
            print("\033[1;31m[!] No data collected.\033[0m")
            input(" Enter...")
            continue

        q = Queue()
        for s in subs:
            q.put(s)

        results = []
        stats = {"done": 0}
        lock = threading.Lock()

        print(f"\n\033[1;33m[+] Verifying {len(subs)} subdomains...\033[0m")

        for _ in range(THREAD_COUNT):
            threading.Thread(
                target=worker,
                args=(q, results, lock, stats, target),
                daemon=True
            ).start()

        while stats["done"] < len(subs):
            with lock:
                sys.stdout.write(
                    f"\r\033[1;30mProgress: {stats['done']}/{len(subs)}\033[0m"
                )
                sys.stdout.flush()
            time.sleep(0.2)

        print("\n\n\033[1;30m================ RESULT ================\033[0m")

        confirmed = [r for r in results if r[0] == "CONFIRMED"]
        potential = [r for r in results if r[0] == "POTENTIAL"]

        if confirmed:
            print(f"\033[1;31m💀 REAL ORIGIN FOUND: {len(confirmed)}\033[0m")
            for _, s, ip, t in confirmed:
                print(f" -> {ip} ({s}) | {t[:60]}")
        elif potential:
            print(f"\033[1;32m⚠ POTENTIAL LEAKS: {len(potential)}\033[0m")
            for _, s, ip, _ in potential:
                print(f" -> {ip} ({s})")
        else:
            print("\033[1;36m✔ FULLY PROXIED / HARD TARGET\033[0m")

        input("\n Press Enter to return to menu...")

# =========================
# ENTRY
# =========================
if __name__ == "__main__":
    print("[!] Load from login.py only")
