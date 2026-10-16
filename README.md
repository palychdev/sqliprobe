# sqliprobe

![version](https://img.shields.io/badge/version-1.0.0-blue)
![python](https://img.shields.io/badge/python-3.8+-green)
![license](https://img.shields.io/badge/license-MIT-green)

сканер **своих** сайтов на sql-инъекции. находит точку, определяет субд,
подтверждает находку повторным запросом. без фейков: если чисто — так и скажет.

```
pip install -r requirements.txt
python -m sqliprobe.cli --url "http://localhost:8000/item?id=1" --consent
python -m sqliprobe.cli --url "http://localhost:8000/news" --consent --crawl
python -m sqliprobe.cli -m targets.txt --consent --threads 5 --html rep.html
```

принимает любые ссылки: с `?id=` и без. без вопросика сам ищет точки:
ссылки с параметрами, get/post формы, куки, числа в пути (`/news/5`).

## ⚠️ только свои сайты

запуск по чужим сайтам без письменного разрешения — уголовка
(ст. 272 УК РФ / CFAA). без флага `--consent` тул не сканирует.
подробно: `docs/LEGAL.md`.

## техники (флаг --technique)

| буква | что | как |
|---|---|---|
| B | boolean-blind | `AND 1=1` / `AND 1=2`, diff страниц |
| E | error-based | кавычки, сигнатуры ошибок 6 субд |
| U | union | `ORDER BY 1..N` → число колонок |
| T | time-based | `SLEEP`/`pg_sleep`/`WAITFOR`/`BENCHMARK` |

дефолт `BEUT` (всё). пример только быстрого: `--technique EU`.

## уровни (флаг --level)

- `1` — get-параметры и числа в пути целевой ссылки
- `2` — плюс формы и куки (дефолт)
- `3` — плюс очередь найденных ссылок (многопоточно, `--threads`)

## остальное

- `--tamper space2comment,randomcase,versioned` — второй проход при подозрении на waf
- waf-детект: cloudflare, ddos-guard, sucuri, modsecurity + факт резки кавычек
- recon: заголовки, куки, `.git/HEAD`, `.env`, robots/sitemap
- `--crawl --max-pages 10` — обход своего хоста
- отчёты: консоль, `--json`, `--html`
- каждая error-находка перепроверяется повторным запросом

## что НЕ делает специально

не сливает таблицы и не выполняет команды — это эксплуатация, а не сканер.
тулы которые «находят на любой ссылке» рисуют ложняки. sqliprobe молчит,
если дыры нет, и это фича.

## стенд для проверки

`python test-server.py` — локальная фейковая дыра. гнать:
`python -m sqliprobe.cli --url "http://127.0.0.1:8765/item?id=1" --consent --delay 0.1`

## файлы

```
sqliprobe/
  cli.py          — аргументы, баннер согласия, bulk
  scanner.py      — ядро, уровни, потоки, куки
  crawler.py      — ссылки/формы/пути
  payloads.py     — пейлоады
  tampers.py      — обход фильтров
  waf.py          — детект waf
  fingerprints.py — сигнатуры ошибок субд
  recon.py        — разведка
  report.py       — консоль/json/html
docs/LEGAL.md
```
