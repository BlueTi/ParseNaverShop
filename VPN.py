import requests
from itertools import cycle

list_proxy = ['socks5://Username:Password@IP1:20000',
              'socks5://Username:Password@IP2:20000',
              'socks5://Username:Password@IP3:20000',
               'socks5://Username:Password@IP4:20000',
              ]

proxy_cycle = cycle(list_proxy)
# Prime the pump
proxy = next(proxy_cycle)

for i in range(1, 10):
    proxy = next(proxy_cycle)
    print(proxy)
    proxies = {
      "http": proxy,
      "https":proxy
    }
    r = requests.get(url='https://ident.me/', proxies=proxies)
    print(r.text)