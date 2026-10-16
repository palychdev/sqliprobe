import argparse
import sys

from . import scanner, report

BANNER = """sqliprobe: сканируй ТОЛЬКО свои сайты или с письменного разрешения.
чужие цели без разрешения = уголовка. флаг --consent это подтверждает."""


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sqliprobe", description="sqli checker for your own sites")
    ap.add_argument("--url", required=True, help="цель: страница, ссылка с ?id= или /news/5")
    ap.add_argument("--consent", action="store_true", help="подтверждаю: сайт мой или есть разрешение")
    ap.add_argument("--delay", type=float, default=1.0, help="пауза между запросами, сек")
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--crawl", action="store_true", help="пройти по ссылкам сайта (только свой хост)")
    ap.add_argument("--max-pages", type=int, default=10, help="лимит страниц при краулинге")
    ap.add_argument("--no-recon", action="store_true", help="без разведки заголовков/файлов")
    ap.add_argument("--json", dest="json_out", default=None, help="куда сохранить отчёт")
    args = ap.parse_args(argv)

    print(BANNER)
    if not args.consent:
        print("без --consent не сканирую. читай docs/LEGAL.md")
        return 2

    try:
        result = scanner.scan(args.url, delay=args.delay, timeout=args.timeout, crawl=args.crawl, max_pages=args.max_pages, recon_on=not args.no_recon)
    except ValueError as e:
        print(f"ошибка: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nостановлено")
        return 130

    report.console(result)
    if args.json_out:
        report.save_json(result, args.json_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
