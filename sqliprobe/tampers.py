import random
import re


def space2comment(payload):
    return payload.replace(" ", "/**/")


def randomcase(payload):
    return "".join(c.upper() if random.random() < 0.5 else c.lower() if c.isalpha() else c for c in payload)


def versioned(payload):
    return re.sub(r"\b(UNION|SELECT|FROM|WHERE|AND|OR|SLEEP)\b",
                  lambda m: f"/*!50000{m.group(1)}*/", payload, flags=re.IGNORECASE)


TAMPERS = {
    "space2comment": space2comment,
    "randomcase": randomcase,
    "versioned": versioned,
}


def apply(payload, names):
    for n in names or []:
        fn = TAMPERS.get(n)
        if fn:
            payload = fn(payload)
    return payload
