import argparse
import sys

from . import scanner, report

BANNER = """sqliprobe 1.0.0: сканируй ТОЛЬКО свои сайты или с письменного разрешения.
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
    ap.add_argument("--technique", default="BEUT", help="техники: B boolean, E error, U union, T time")
    ap.add_argument("--level", type=int, default=2, help="1: get+путь, 2: +формы и куки, 3: +краул очереди")
    ap.add_argument("--tamper", default="", help="через запятую: space2comment,randomcase,versioned")
    ap.add_argument("--threads", type=int, default=3, help="потоки для очереди ссылок")
    ap.add_argument("-m", dest="bulk", default=None, help="файл со списком url")
    ap.add_argument("--json", dest="json_out", default=None, help="куда сохранить отчёт")
    ap.add_argument("--html", dest="html_out", default=None, help="html-отчёт")
    args = ap.parse_args(argv)

    print(BANNER)
    if not args.consent:
        print("без --consent не сканирую. читай docs/LEGAL.md")
        return 2

    targets = [args.url]
    if args.bulk:
        with open(args.bulk, encoding="utf-8") as fh:
            targets = [l.strip() for l in fh if l.strip().startswith("http")]

    results = []
    try:
        for t in targets:
            results.append(scanner.scan(t, delay=args.delay, timeout=args.timeout,
                                        crawl=args.crawl, max_pages=args.max_pages,
                                        recon_on=not args.no_recon, technique=args.technique,
                                        level=args.level,
                                        tampers=[x.strip() for x in args.tamper.split(",") if x.strip()],
                                        threads=args.threads))
    except ValueError as e:
        print(f"ошибка: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nостановлено")
        return 130

    for result in results:
        report.console(result)
        if args.json_out:
            report.save_json(result, args.json_out)
        if args.html_out:
            report.save_html(result, args.html_out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
