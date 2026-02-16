import requests

def scrape_proxies():
    # Daftar sumber proxy gratis yang terupdate setiap menit
    sources = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://www.proxy-list.download/api/v1/get?type=http",
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    ]
    
    print("[*] Sedang mengambil amunisi proxy...")
    proxy_list = []
    
    for url in sources:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                proxies = r.text.split('\r\n')
                proxy_list.extend(proxies)
        except:
            continue
            
    # Simpan ke file
    with open("proxy.txt", "w") as f:
        for proxy in set(proxy_list): # set() untuk hapus duplikat
            if proxy:
                f.write(proxy + "\n")
                
    print(f"[+] Berhasil mendapatkan {len(proxy_list)} proxy! (Simpan di proxy.txt)")

if __name__ == "__main__":
    scrape_proxies()
