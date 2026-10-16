import json


def console(result):
    print(f"target: {result['url']} (base http {result['base_status']})")
    if not result["findings"]:
        print("sqli: ничего. либо чисто, либо waf съел пейлоады.")
    for f in result["findings"]:
        extra = f.get("dbms", "")
        print(f"[{f['type']}] param={f['param']} {extra} payload={f.get('payload', '-')}")
    if result.get("recon"):
        print("recon:")
        for r in result["recon"]:
            print(f"  - {r['item']}")


def save_json(result, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=2)
    print(f"отчёт: {path}")


def save_html(result, path):
    rows = "".join(
        f"<tr><td>{f['type']}</td><td>{f['param']}</td><td>{f.get('dbms', '')}</td>"
        f"<td>{f.get('payload', '-')}</td><td>{'yes' if f.get('confirmed') else ''}</td></tr>"
        for f in result["findings"]
    )
    recon = "".join(f"<li>{r['item']}</li>" for r in result.get("recon", []))
    html = (f"<meta charset=utf-8><title>sqliprobe {result['url']}</title>"
            f"<h1>{result['url']} (http {result['base_status']})</h1>"
            "<table border=1><tr><th>type</th><th>param</th><th>dbms</th><th>payload</th><th>confirmed</th></tr>"
            f"{rows}</table><h2>recon</h2><ul>{recon}</ul>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    print(f"отчёт: {path}")
