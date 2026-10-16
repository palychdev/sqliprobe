import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import requests

from . import payloads, fingerprints, crawler

UA = {"User-Agent": "sqliprobe/0.2"}


def get(url, timeout):
    r = requests.get(url, timeout=timeout, headers=UA)
    return r.status_code, r.text, r.elapsed.total_seconds()


def post(url, data, timeout):
    r = requests.post(url, data=data, timeout=timeout, headers=UA)
    return r.status_code, r.text, r.elapsed.total_seconds()


def split_params(url):
    return parse_qs(urlparse(url).query, keep_blank_values=True)


def build_url(parts, params):
    return urlunparse((parts.scheme, parts.netloc, parts.path, parts.params, urlencode(params, doseq=True), parts.fragment))


def check_value(label, orig, send, findings, base_body, base_status, delay, timeout):
    for pl in payloads.ERROR_TESTS:
        try:
            st, body, _ = send(orig + pl)
        except requests.RequestException as e:
            findings.append({"param": label, "type": "request-error", "detail": str(e)[:120]})
            continue
        dbms = fingerprints.fingerprint(body)
        if dbms or (st == 500 and st != base_status):
            findings.append({"param": label, "type": "error-based", "payload": pl, "dbms": dbms or "unknown", "status": st})
        time.sleep(delay)

    for true_pl, false_pl in payloads.BOOLEAN_PAIRS:
        try:
            _, t_body, _ = send(orig + true_pl)
            time.sleep(delay)
            _, f_body, _ = send(orig + false_pl)
        except requests.RequestException:
            continue
        if abs(len(t_body) - len(f_body)) > max(50, len(base_body) * 0.05):
            findings.append({"param": label, "type": "boolean-based", "payload": f"{true_pl} / {false_pl}"})
        time.sleep(delay)

    for pl, secs, dbms in payloads.TIME_PAYLOADS:
        try:
            _, _, elapsed = send(orig + pl, timeout + secs + 5)
        except requests.RequestException:
            continue
        if elapsed >= secs - 1:
            findings.append({"param": label, "type": "time-based", "payload": pl, "dbms": dbms, "slept": round(elapsed, 1)})
        time.sleep(delay)


def scan_get_params(url, delay, timeout):
    parts = urlparse(url)
    params = split_params(url)
    if not params:
        raise ValueError("в url нет get-параметров")
    try:
        base_status, base_body, _ = get(build_url(parts, params), timeout)
    except requests.RequestException:
        raise ValueError("цель не отвечает, проверь url и что сервер поднят")
    findings = []
    for name in params:
        orig = params[name][0]

        def send(v, to=timeout, n=name):
            cp = {k: list(val) for k, val in params.items()}
            cp[n] = [v]
            return get(build_url(parts, cp), to)

        check_value(f"{url} :: {name}", orig, send, findings, base_body, base_status, delay, timeout)
    return findings, base_status


def scan_path(url, delay, timeout):
    findings = []
    for i, seg in crawler.path_targets(url):
        try:
            base_status, base_body, _ = get(url, timeout)
        except requests.RequestException:
            raise ValueError("цель не отвечает, проверь url и что сервер поднят")

        def send(v, to=timeout, idx=i):
            p = urlparse(url)
            segs = p.path.strip("/").split("/")
            segs[idx] = v
            u = urlunparse((p.scheme, p.netloc, "/" + "/".join(segs), p.params, p.query, p.fragment))
            return get(u, to)

        check_value(f"{url} :: path[{i}]", seg, send, findings, base_body, base_status, delay, timeout)
    return findings


def scan_post_form(form, delay, timeout):
    try:
        base_status, base_body, _ = post(form["action"], form["fields"], timeout)
    except requests.RequestException:
        raise ValueError("цель не отвечает, проверь url и что сервер поднят")
    findings = []
    for name in form["fields"]:
        orig = form["fields"][name]

        def send(v, to=timeout, n=name):
            data = dict(form["fields"])
            data[n] = v
            return post(form["action"], data, to)

        check_value(f"{form['action']} :: {name} (POST)", orig, send, findings, base_body, base_status, delay, timeout)
    return findings


def scan(url, delay=1.0, timeout=15, crawl=False, max_pages=10):
    findings = []
    base_status = None
    tested = set()

    if split_params(url):
        f, base_status = scan_get_params(url, delay, timeout)
        findings += f
        tested.add(url)

    f = scan_path(url, delay, timeout)
    findings += f

    try:
        _, page, _ = get(url, timeout)
    except requests.RequestException:
        raise ValueError("цель не отвечает, проверь url и что сервер поднят")
    if base_status is None:
        base_status = 200

    pts = crawler.discover(url, page)
    for form in pts["post_forms"]:
        findings += scan_post_form(form, delay, timeout)

    queue = [u for u in pts["links"] if u not in tested][:max_pages]
    if crawl:
        seen = set(tested)
        depth = [url]
        while depth and len(seen) < max_pages:
            nxt = []
            for page_url in depth:
                try:
                    _, html, _ = get(page_url, timeout)
                except requests.RequestException:
                    continue
                for u in crawler.discover(page_url, html)["links"]:
                    if u not in seen and u not in tested:
                        seen.add(u)
                        queue.append(u)
                        nxt.append(u)
                    if len(seen) >= max_pages:
                        break
            depth = nxt
            time.sleep(delay)

    for u in queue[:max_pages]:
        try:
            f, _ = scan_get_params(u, delay, timeout)
            findings += f
        except ValueError:
            continue

    return {"url": url, "base_status": base_status, "findings": findings}
