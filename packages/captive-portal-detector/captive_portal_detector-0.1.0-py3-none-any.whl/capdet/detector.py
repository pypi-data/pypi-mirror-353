"""
IMPORTANT: This connectivity check assumes any TLS handshake that succeeds with a certificate trusted by the OS equals real Internet access.
Networks that install their own root CA and proxy HTTPS (corporate MITM, some campus firewalls) will be reported as OK, even though traffic is being intercepted.
Standard captive portals, DNS hijacks, and HTTP-only walled gardens are still caught.
TODO: If we need to detect corporate MITM proxies we'll need to add certificate-pinning or another out-of-band trust test.
"""

import concurrent.futures as cf
import hashlib
import random
import re
import socket
import time
from ipaddress import ip_address

import requests


class NetworkProbe:
    """
    Probes network connectivity and captive portal detection.
    Uses multiple methods to determine if the network is reachable or if a captive portal is present.
    """
    def __init__(self, _last_run=0, _last_res="NO_INTERNET"):
        self.logger = None
        self._last_run = _last_run
        self._last_res = _last_res

    PRIMARY = "http://clients3.google.com/generate_204"
    FALLBACK = "http://detectportal.firefox.com/success.txt"
    # HTTPS_PIN_HOST  = "www.example.com"
    HTTPS_PROBE_HOST = "www.cloudflare.com"
    IPV6_PLAIN = "http://[2606:4700:4700::1111]/"   # reachability only
    TIMEOUT = 5
    CACHE_TTL = 30

    _expected = {
        PRIMARY:  hashlib.sha256(b"").hexdigest(),
        FALLBACK: hashlib.sha256(b"success\n").hexdigest(),
    }

    _meta  = re.compile(rb"<meta[^>]+http-equiv=['\"]?refresh", re.I)
    _jsloc = re.compile(rb"location\.(href|replace)", re.I)

    def _hash(self, b):    return hashlib.sha256(b).hexdigest()
    def _private(self, ip): return ip_address(ip).is_private

    def _cert_sha256(self, sock):
        der = sock.getpeercert(binary_form=True)
        return hashlib.sha256(der).hexdigest()

    def _https_probe(self, hostname: str, timeout: int = TIMEOUT) -> str:
        """Try a plain TLS handshake; success ⇒ 'OK', failure ⇒ 'CAPTIVE'."""
        import ssl, socket

        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout) as raw:
                with ctx.wrap_socket(raw, server_hostname=hostname):
                    pass
            return "OK"
        except (socket.timeout, socket.gaierror,
                ssl.SSLError, ConnectionRefusedError, OSError):
            return "CAPTIVE"

    def _random_host(self):
        return f"https://{random.randint(0,2**32):x}.example.net/"

    def _single(self, url):
        try:
            r = requests.get(url, timeout=self.TIMEOUT, allow_redirects=False,
                             headers={"User-Agent":"PinguinProbe"},
                             proxies={"http":None,"https":None}, verify=False)
        except requests.exceptions.Timeout:
            # one slow-link retry
            try:
                r = requests.get(url, timeout=self.TIMEOUT*2, allow_redirects=False,
                                 headers={"User-Agent":"PinguinProbe"},
                                 proxies={"http":None,"https":None}, verify=False)
            except requests.exceptions.Timeout:
                return "CAPTIVE"
        except requests.exceptions.ConnectionError:
            return "NO_INTERNET"

        if url in self._expected and self._hash(r.content) == self._expected[url] and r.status_code in (200,204):
            return "OK"

        if r.status_code in (301,302,303,307,308):
            return "CAPTIVE"

        if r.status_code == 200 and (self._meta.search(r.content) or self._jsloc.search(r.content)):
            return "CAPTIVE"

        return "UNKNOWN"  # 200 with unexpected body, or other weird code

    def network_health(self, force=False):
        if not force and time.time() - self._last_run < self.CACHE_TTL:
            return self._last_res

        # pin_sha256 = None
        # # preload the expected cert hash once
        # if not pin_sha256:
        #     ctx = ssl.create_default_context()
        #     with socket.create_connection(("www.example.com",443), self.TIMEOUT) as s:
        #         with ctx.wrap_socket(s,server_hostname="www.example.com") as tls:
        #             pin_sha256 = self._cert_sha256(tls)

        probes = {
            "primary":  self.PRIMARY,
            "fallback": self.FALLBACK,
            "ipv6":     self.IPV6_PLAIN,
            "random":   self._random_host(),
        }

        with cf.ThreadPoolExecutor(max_workers=len(probes) + 1) as pool:
            futs = {pool.submit(self._single, url): tag for tag, url in probes.items()}
            futs[pool.submit(self._https_probe, self.HTTPS_PROBE_HOST)] = "tls"

        res = {k: f.result() for f,k in futs.items()}

        # DNS spoof check
        try:
            ips = {a[-1][0] for a in socket.getaddrinfo("clients3.google.com", 80)}
            if any(self._private(ip) for ip in ips):
                res["dns"] = "CAPTIVE"
        except socket.gaierror:
            res["dns"] = "CAPTIVE"

        verdict = "CAPTIVE" if "CAPTIVE" in res.values() \
            else "OK"       if "OK" in res.values() \
            else "NO_INTERNET"

        _last_run = time.time()
        _last_res = verdict
        return verdict
