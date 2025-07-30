from re import findall

def get_vars(j2: str) -> dict[str, str]:
    pattern: str = r'(?<!\\){%[ \n]*[_a-zA-Z][_a-zA-Z0-9]*[ \n]*[^\\]%}'
    matches: list[str] = findall(pattern=pattern, string=j2)
    return { var[2:-2].strip(): var for var in matches }

def substitute(j2: str,
                subs: dict[str, str],
                vars: dict[str, str]) -> str:
    result: str = j2
    for name, sub in subs.items():
        result = result.replace(vars[name], sub)
    return result