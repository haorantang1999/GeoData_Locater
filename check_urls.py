#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import sys
import json
import time
import threading
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

MD_PATH = Path("F:/Automation/国内遥感数据网站合集/国内外地理遥感数据网站合集.md")
text = MD_PATH.read_text(encoding="utf-8")

URL_PATTERN = re.compile(r"<(https?://[^>]+)>|https?://[^\s<>\"'\)\]\，]+", re.IGNORECASE)
urls = set()
for m in URL_PATTERN.finditer(text):
    url = m.group(0).strip("<>")
    if url.startswith("http"):
        urls.add(url)

print("[*] Found " + str(len(urls)) + " unique URLs")
urls = sorted(urls)

TIMEOUT = 15
MAX_WORKERS = 10
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

results = {
    "ok": [],
    "redirect": [],
    "client_error": [],
    "server_error": [],
    "timeout": [],
    "connection_error": [],
    "other": [],
}
lock = threading.Lock()


def check(url):
    try:
        r = requests.head(url, timeout=TIMEOUT, allow_redirects=True, headers={"User-Agent": UA})
        if r.status_code in (405, 501, 403) or r.status_code >= 400:
            r = requests.get(url, timeout=TIMEOUT, allow_redirects=True, stream=True, headers={"User-Agent": UA})
            r.close()
        return url, r.status_code, r.url
    except requests.exceptions.Timeout:
        return url, "timeout", ""
    except requests.exceptions.ConnectionError:
        return url, "conn_err", ""
    except requests.exceptions.SSLError:
        return url, "ssl_err", ""
    except Exception as e:
        return url, "other", str(e)[:100]


def main():
    print("[*] Testing with " + str(MAX_WORKERS) + " workers, timeout=" + str(TIMEOUT) + "s")
    start = time.time()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(check, u): u for u in urls}
        for i, f in enumerate(as_completed(futures), 1):
            url, status, final = f.result()
            with lock:
                if isinstance(status, int):
                    if 200 <= status < 300:
                        results["ok"].append((url, status, final))
                    elif 300 <= status < 400:
                        results["redirect"].append((url, status, final))
                    elif 400 <= status < 500:
                        results["client_error"].append((url, status, final))
                    else:
                        results["server_error"].append((url, status, final))
                elif status == "timeout":
                    results["timeout"].append((url, "", ""))
                elif status in ("conn_err", "ssl_err"):
                    results["connection_error"].append((url, "", ""))
                else:
                    results["other"].append((url, "", ""))
            if i % 50 == 0:
                print("  Progress: " + str(i) + "/" + str(len(urls)))
    elapsed = time.time() - start
    print("\n[*] Done: " + str(len(urls)) + " URLs in " + str(round(elapsed, 1)) + "s\n")

    print("OK 2xx:           " + str(len(results["ok"])))
    print("REDIRECT 3xx:     " + str(len(results["redirect"])))
    print("4xx CLIENT ERR:   " + str(len(results["client_error"])))
    print("5xx SERVER ERR:   " + str(len(results["server_error"])))
    print("TIMEOUT:          " + str(len(results["timeout"])))
    print("CONN/SSL ERR:     " + str(len(results["connection_error"])))
    print("OTHER:            " + str(len(results["other"])))
    print()

    suspicious = (results["client_error"] + results["server_error"] +
                   results["timeout"] + results["connection_error"] + results["other"])
    if suspicious:
        print("=== " + str(len(suspicious)) + " URLs need attention ===\n")
        for url, status, final in suspicious[:200]:
            print("  [" + str(status) + "] " + url)
            if final and final != url:
                print("        -> " + final)
        if len(suspicious) > 200:
            more = len(suspicious) - 200
            print("  ... and " + str(more) + " more")

    out = Path("F:/Automation/国内遥感数据网站合集/url_check_result.json")
    out.write_text(json.dumps({
        "total": len(urls),
        "ok": [{"url": u, "status": s, "final": f} for u, s, f in results["ok"]],
        "redirect": [{"url": u, "status": s, "final": f} for u, s, f in results["redirect"]],
        "client_error": [{"url": u, "status": s, "final": f} for u, s, f in results["client_error"]],
        "server_error": [{"url": u, "status": s, "final": f} for u, s, f in results["server_error"]],
        "timeout": [{"url": u} for u, _, _ in results["timeout"]],
        "connection_error": [{"url": u} for u, _, _ in results["connection_error"]],
        "other": [{"url": u} for u, _, _ in results["other"]],
    }, ensure_ascii=False, indent=2))
    print("\nDetails saved to: " + str(out))


if __name__ == "__main__":
    main()
