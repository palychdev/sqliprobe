import requests

UA = {"User-Agent": "sqliprobe/0.2"}


def headers_audit(url, timeout):
    out = []
    try:
        r = requests.get(url, timeout=timeout, headers=UA)
    except requests.RequestException:
        return [{"item": "target unreachable for recon"}]
    h = {k.lower(): v for k, v in r.headers.items()}
    server = h.get("server", "")
    if server:
        out.append({"item": f"server header: {server}"})
    powered = h.get("x-powered-by", "")
    if powered:
        out.append({"item": f"x-powered-by: {powered} (version disclosure)"})
    for sec in ("content-security-policy", "x-frame-options", "strict-transport-security", "x-content-type-options"):
        if sec not in h:
            out.append({"item": f"missing security header: {sec}"})
    cookies = h.get("set-cookie", "")
    if cookies:
        low = cookies.lower()
        if "httponly" not in low:
            out.append({"item": "cookie without HttpOnly"})
        if "secure" not in low and url.startswith("https"):
            out.append({"item": "cookie without Secure on https"})
        if "samesite" not in low:
            out.append({"item": "cookie without SameSite"})
    return out


def exposed_files(base, timeout):
    from urllib.parse import urljoin
    out = []
    for path, what in ((".git/HEAD", "git repo exposed"), ("robots.txt", "robots.txt present"), ("sitemap.xml", "sitemap.xml present"), (".env", ".env exposed")):
        try:
            r = requests.get(urljoin(base, path), timeout=timeout, headers=UA)
        except requests.RequestException:
            continue
        if path == ".git/HEAD" and r.status_code == 200 and "ref:" in r.text:
            out.append({"item": ".git/HEAD exposed — repo readable"})
        elif path == ".env" and r.status_code == 200 and "=" in r.text:
            out.append({"item": ".env exposed"})
        elif path in ("robots.txt", "sitemap.xml") and r.status_code == 200:
            interesting = [l.strip() for l in r.text.splitlines() if l.strip().lower().startswith("disallow:") and l.strip() != "Disallow:"]
            out.append({"item": f"{path} ({len(interesting)} disallowed)" if interesting else path})
            out += [{"item": f"robots hides: {d}"} for d in interesting[:10]]
    return out


def run(url, timeout):
    from urllib.parse import urlparse
    base = f"{urlparse(url).scheme}://{urlparse(url).netloc}/"
    return headers_audit(url, timeout) + exposed_files(base, timeout)
