"""Read-only connectivity probes. Does not log in, change proxy settings, or collect credentials."""
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

URLS = [
    'https://wokwi.com/status',
    'https://wokwi.com/login',
    'https://identitytoolkit.googleapis.com/',
    'https://securetoken.googleapis.com/',
]

def probe(item):
    mode, url = item
    started = time.monotonic()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({} if mode == 'direct' else None))
    result = {'mode': mode, 'url': url}
    try:
        with opener.open(urllib.request.Request(url, headers={'User-Agent': 'STM32-Connectivity-Check/1.0'}), timeout=8) as response:
            result.update(transport='HTTP_RESPONSE', http_status=response.status)
    except urllib.error.HTTPError as error:
        result.update(transport='HTTP_RESPONSE', http_status=error.code)
    except Exception as error:
        # Exception messages may contain proxy hosts; do not store them.
        reason = getattr(error, 'reason', error)
        result.update(transport='FAILED', error_type=type(reason).__name__)
    result['seconds'] = round(time.monotonic() - started, 2)
    return result

if __name__ == '__main__':
    proxies = urllib.request.getproxies()
    items = [(mode, url) for mode in ['direct', 'system_or_environment_proxy'] for url in URLS]
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(probe, items))
    report = {'time': time.time(), 'proxy_detected': bool(proxies), 'results': results,
              'scope': 'Public HTTP connectivity only; no browser authentication or credentials tested. HTTP 4xx still proves a response, not successful login.'}
    path = Path(__file__).resolve().parents[1] / 'logs/login_network.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
