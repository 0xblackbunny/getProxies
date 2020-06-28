import requests
from bs4 import BeautifulSoup
from multiprocessing import Pool
import os.path
#import timeit

POOL = 60
TIMEOUT = 3

URL = [
"https://www.sslproxies.org/",
"https://free-proxy-list.net/",
"https://free-proxy-list.net/anonymous-proxy.html",
"https://free-proxy-list.net/uk-proxy.html",
"https://www.us-proxy.org/"
]

checkerURL = "https://1.1.1.1"
proxyFile = "proxies.txt"
proxyList = []
cleanProxyList = []


def collect():
    #print('Collecting proxies.')

    global proxyList
    for site in URL:
        page = requests.get(site)
        soup = BeautifulSoup(page.text, 'html.parser')

        for proxyData in soup.select("#proxylisttable > tbody tr"):
            proxyIP = proxyData.select('td')[0].text
            proxyPORT = proxyData.select('td')[1].text
            p = f'{proxyIP}:{proxyPORT}'

            proxyList.append(p)


def checker(p):
    #print(f'Checking {p}')

    global cleanProxyList

    proxies = {
        "http" : f'http://{p}',
        "https" : f'https://{p}'
    }

    try:
        page = requests.get(checkerURL, proxies=proxies, timeout=TIMEOUT)
        if page.status_code == 200:
            with open(proxyFile, 'a') as f:
                    f.writelines(f'{p}\n')
            print(p)

    except (requests.exceptions.ProxyError,
        requests.exceptions.SSLError,
        requests.exceptions.ConnectionError) as e: pass #print(f'[Err] - {e}')


def check():
    #print('Checking proxies. This might take some time.')

    processes = []
    pool = Pool(POOL)

    for proxy in proxyList:
        processes.append(pool.apply_async(checker, args=(proxy,)))

    pool.close()
    pool.join()


def backup():
    #print('Resetting proxy file and backup old cycle data.')

    if os.path.isfile(proxyFile):
        with open(proxyFile, 'r') as pf:
            proxies = pf.read()
            with open('proxies_backup.txt','a') as pb:
                pb.write(proxies)
        with open(proxyFile, 'w') as pf:
            pf.write('')


def main():
    #start = timeit.default_timer()

    backup()
    collect()
    check()

    #stop = timeit.default_timer()
    #print(f'[OK] {round(stop - start)} seconds.')  


if __name__ == '__main__':
    try: main()
    except: pass
