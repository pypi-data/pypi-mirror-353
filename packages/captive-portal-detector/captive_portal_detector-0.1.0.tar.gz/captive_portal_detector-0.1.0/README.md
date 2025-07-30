# Captive Portal Detector

A Python utility to detect captive portals and assess real internet connectivity.

## Features

- Checks standard captive portals, DNS hijacks, HTTP-only walled gardens
- Uses multiple probes (HTTP/HTTPS/IPv6/DNS)
- Detects TLS interception in limited cases
- Fast: runs probes concurrently

## Usage

Install via pip:

```bash
pip install captive-portal-detector
```

### CLI Usage
Simply run it with:
```capdet```

### Python Usage
```python
from capdet.detector import NetworkProbe

status = NetworkProbe().network_health()
print(status)
```

## Output
```
OK           → Internet access confirmed
CAPTIVE      → Captive portal or DNS hijack detected
NO_INTERNET  → No network connectivity
```

## Notes
- Any successful TLS handshake is considered "OK"
- Networks with MITM TLS proxies (e.g., corporate firewalls) may be incorrectly classified as "OK"
- For true MITM detection, certificate pinning would be required (not implemented)

## TODO
Certificate pinning to detect HTTPS MITM proxies
