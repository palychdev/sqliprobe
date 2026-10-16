import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests

from . import payloads, fingerprints


def split_url(url):
    p = urlparse(url)
    q = parse_qs(p.query, keep_blank_values=True)
    if not q:
        raise ValueError("в url нет get-параметров, тестировать нечего")
    return p, q


def build_url(parts, params):
    return urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, urlencode(params, doseq=True), parts.fragment))


def get(url, timeout):
    r = requests.get(url, timeout=timeout, headers={"User-Agent": "sqliprobe/0.1"})
    return r.status_code, r.text, r.elapsed.total_seconds()


def scan(url, delay=1.0, timeout=15, time_sleep=5):
    parts, params = split_url(url)
    findings = []
    base_status, base_body, _ = get(build_url(parts, params), timeout)

    for name in params:
        orig = params[name][0]

        for pl in payloads.ERROR_TESTS:
            params[name] = [orig + pl]
            try:
                st, body, _ = get(build_url(parts, params), timeout)
            except requests.RequestException as e:
                findings.append({"param": name, "type": "request-error", "detail": str(e)[:120]})
                continue
            dbms = fingerprints.fingerprint(body)
            if dbms or (st == 500 and st != base_status):
                findings.append({
                    "param": name,
                    "type": "error-based",
                    "payload": pl,
                    "dbms": dbms or "unknown",
                    "status": st,
                })
            time.sleep(delay)

        for true_pl, false_pl in payloads.BOOLEAN_PAIRS:
            try:
                params[name] = [orig + true_pl]
                _, t_body, _ = get(build_url(parts, params), timeout)
                time.sleep(delay)
                params[name] = [orig + false_pl]
                _, f_body, _ = get(build_url(parts, params), timeout)
            except requests.RequestException:
                continue
            if abs(len(t_body) - len(f_body)) > max(50, len(base_body) * 0.05):
                findings.append({"param": name, "type": "boolean-based", "payload": f"{true_pl} / {false_pl}"})
            time.sleep(delay)

        for pl, secs, dbms in payloads.TIME_PAYLOADS:
            params[name] = [orig + pl]
            try:
                _, _, elapsed = get(build_url(parts, params), timeout + secs + 5)
            except requests.RequestException:
                continue
            if elapsed >= secs - 1:
                findings.append({"param": name, "type": "time-based", "payload": pl, "dbms": dbms, "slept": round(elapsed, 1)})
            time.sleep(delay)

        params[name] = [orig]

    return {"url": url, "base_status": base_status, "findings": findings}
