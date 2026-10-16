SIGNATURES = {
    "mysql": [
        "you have an error in your sql syntax",
        "mysql_fetch",
        "mysqli_",
        "supplied argument is not a valid mysql",
    ],
    "postgres": [
        "pg_query()",
        "postgresql",
        "psql:",
        "unterminated quoted string",
    ],
    "mssql": [
        "microsoft ole db provider for sql server",
        "odbc sql server driver",
        "unclosed quotation mark",
    ],
    "sqlite": [
        "sqlite3::",
        "sqlite error",
        "near \"syntax error\"",
    ],
    "oracle": [
        "ora-01756",
        "ora-00933",
        "oracle error",
    ],
}


def fingerprint(body):
    low = body.lower()
    for dbms, sigs in SIGNATURES.items():
        for s in sigs:
            if s in low:
                return dbms
    return None
