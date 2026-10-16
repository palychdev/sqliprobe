import requests

UA = {"User-Agent": "sqliprobe/0.2"}
BLOCK_CODES = {403, 406, 429, 451, 501, 503}
WAF_HEADERS = {
    "cf-ray": "cloudflare",
    "cf-mitigated": "cloudflare",
    "x-sucuri-id": "sucuri",
    "x-protected-by": None,
}


def detect(url, timeout):
    try:
        base = requests.get(url, timeout=timeout, headers=UA)
        probe = requests.get(url + ("&" if "?" in url else "?") + "x=%27", timeout=timeout, headers=UA)
    except requests.RequestException:
        return {"waf": None, "blocked": False}
    h = {k.lower(): (v or "") for k, v in probe.headers.items()}
    server = (h.get("server", "") + " " + base.headers.get("Server", "")).lower()
    for marker, name in (("cloudflare", "cloudflare"), ("ddos-guard", "ddos-guard"),
                         ("sucuri", "sucuri"), ("incapsula", "incapsula"),
                         ("mod_security", "modsecurity"), ("f5", "big-ip"),
                         ("akamai", "akamai")):
        if marker in server:
            return {"waf": name, "blocked": probe.status_code in BLOCK_CODES}
    for hdr, name in WAF_HEADERS.items():
        if hdr in h:
            return {"waf": name or h[hdr], "blocked": probe.status_code in BLOCK_CODES}
    if probe.status_code in BLOCK_CODES and base.status_code not in BLOCK_CODES:
        return {"waf": "unknown (blocks quotes)", "blocked": True}
    return {"waf": None, "blocked": False}
