import re
from pathlib import Path


def merge(src: dict, dst: dict):
    """
    Deep merge two dictionaries

    >>> a = {'first': {'rows': {'pass': 'dog', 'num': '1'}}}
    >>> b = {'first': {'rows': {'fail': 'cat', 'num': '5'}}}
    >>> merge(b, a) == {'first': {'rows': {'pass': 'dog', 'fail': 'cat', 'num': '5'}}}
    True
    """
    for key, value in src.items():
        if isinstance(value, dict):
            node = dst.setdefault(key, {})
            merge(value, node)
        else:
            dst[key] = value
    return dst


def parse_conf(conf: Path) -> dict:
    cfg = {}
    stack = []
    element = cfg
    with open(conf) as f:
        for line in f:
            line = line.strip()
            if re.match(r'^#', line):
                continue  # skip comment
            if tag := re.search(r'^<\w*>', line):
                name = tag[0].strip('<>')
                new_element = {}
                element[name] = new_element
                stack.append(element)
                element = new_element
            elif re.search(r'^</\w*>', line):
                element = stack.pop()
            elif re.search(r'^[-/.\w\s]+=[-/.\w\s]*', line):
                param = line.split('=', 2)
                element[param[0].strip()] = (param[1] or '').strip()

    if inc := cfg.get('include_dir', ''):
        inc = Path(conf.parent, inc)
        if inc.is_file():
            inc_cfg = parse_conf(inc)
            cfg = merge(cfg, inc_cfg)
        elif inc.is_dir():
            for f in inc.rglob('*.conf'):
                inc_cfg = parse_conf(f)
                cfg = merge(inc_cfg, cfg)

    return cfg
