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
