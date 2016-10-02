import netifaces
import requests


class IPFinder(object):
    @property
    def public_ip(self):
        r = requests.get("https://icanhazip.com")
        return r.text.strip()

    @property
    def local_ips(self):
        for iface in netifaces.interfaces():
            addresses = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addresses:
                for addr in addresses[netifaces.AF_INET]:
                    yield iface, addr["addr"]
