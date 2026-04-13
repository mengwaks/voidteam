#!/usr/bin/env python3
# REVIP CLI - Termux Version
# Reverse IP & Domain → IP

import requests
import re
import socket
import threading
import os
from multiprocessing.dummy import Pool
from datetime import datetime

# ─── CONFIG ───────────────────────────────
THREAD_DEFAULT = 10
D2IP_THREAD_DEFAULT = 50

# warna terminal
class C:
    G = "\033[92m"
    R = "\033[91m"
    Y = "\033[93m"
    C = "\033[96m"
    P = "\033[95m"
    W = "\033[0m"

# ─── LOG ─────────────────────────────────
def log(msg, color=C.W):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"{C.Y}[{ts}]{C.W} {color}{msg}{C.W}")

# ─── CLEAN DOMAIN ────────────────────────
def clean_domain(site):
    site = re.sub(r'^https?://', '', site)
    site = site.replace('www.', '')
    site = site.split('/')[0].rstrip('/')
    return site

# ─── REVERSE IP ──────────────────────────
def revip(ip_list, threads):
    results = set()

    def add(domain):
        if domain not in results:
            results.add(domain)
            print(f"{C.G}{domain}{C.W}")
            with open("Grabbed.txt", "a") as f:
                f.write(domain + "\n")

    def api1(ip):
        try:
            url = f"https://rapiddns.io/s/{ip}?full=1&down=1#result"
            data = requests.get(url, timeout=10, verify=False).text
            found = re.findall(
                r'<td>(?!\-)(?:[a-zA-Z\d\-]{0,62}[a-zA-Z\d]\.){1,126}(?!\d+)[a-zA-Z]{1,63}</td>',
                data)[3:]

            for d in found:
                d = d.replace('<td>', '').replace('</td>', '').replace('www.', '')
                add(d)
        except:
            pass

    def api2(ip):
        try:
            url = f"https://api.webscan.cc/?action=query&ip={ip}"
            data = requests.get(url, timeout=10, verify=False).text
            found = re.findall(r'"domain": "(.*?)",', data)[3:]

            for d in found:
                d = d.replace('www.', '')
                add(d)
        except:
            pass

    def api3(ip):
        try:
            url = f"http://main-srv.xreverselabs.my.id:1337/reverse-ip?apikey=unknown&ip={ip}"
            data = requests.get(url, timeout=10).text
            found = re.findall(r'"(.*?)"', data)[3:]

            for d in found:
                d = d.replace('www.', '')
                add(d)
        except:
            pass

    def worker(ip):
        api1(ip)
        api2(ip)
        api3(ip)

    log(f"Start Reverse IP ({len(ip_list)} target)", C.C)

    pool = Pool(threads)
    pool.map(worker, ip_list)
    pool.close()
    pool.join()

    log(f"Done! Total domain: {len(results)}", C.G)

# ─── DOMAIN → IP ─────────────────────────
def d2ip(domain_list, threads):
    results = []

    def worker(raw):
        try:
            dom = clean_domain(raw)
            try:
                ip = socket.gethostbyname(dom)
                results.append((dom, ip))
                print(f"{C.G}{dom} → {ip}{C.W}")
                with open("IPs.txt", "a") as f:
                    f.write(ip + "\n")
            except:
                print(f"{C.R}{dom} → FAIL{C.W}")
        except:
            pass

    log(f"Start Domain → IP ({len(domain_list)} target)", C.C)

    pool = Pool(threads)
    pool.map(worker, domain_list)
    pool.close()
    pool.join()

    log(f"Done! {len(results)} success", C.G)

# ─── MAIN MENU ───────────────────────────
def main():
    print(f"""
{C.P}██████╗ ███████╗██╗   ██╗██╗██████╗
██╔══██╗██╔════╝██║   ██║██║██╔══██╗
██████╔╝█████╗  ██║   ██║██║██████╔╝
██╔══██╗██╔══╝  ╚██╗ ██╔╝██║██╔═══╝
██║  ██║███████╗ ╚████╔╝ ██║██║
╚═╝  ╚═╝╚══════╝  ╚═══╝  ╚═╝╚═╝{C.W}

{C.C}Reverse IP & Domain Tool (CLI){C.W}
""")

    print("1. Reverse IP")
    print("2. Domain → IP")
    print("0. Exit")

    choice = input("\nPilih: ")

    if choice == "1":
        path = input("File list IP: ")
        if not os.path.exists(path):
            log("File tidak ditemukan!", C.R)
            return

        with open(path) as f:
            ips = [x.strip() for x in f if x.strip()]

        th = input(f"Threads ({THREAD_DEFAULT}): ")
        th = int(th) if th else THREAD_DEFAULT

        revip(ips, th)

    elif choice == "2":
        path = input("File list domain: ")
        if not os.path.exists(path):
            log("File tidak ditemukan!", C.R)
            return

        with open(path) as f:
            domains = [x.strip() for x in f if x.strip()]

        th = input(f"Threads ({D2IP_THREAD_DEFAULT}): ")
        th = int(th) if th else D2IP_THREAD_DEFAULT

        d2ip(domains, th)

    else:
        exit()

if __name__ == "__main__":
    main()
