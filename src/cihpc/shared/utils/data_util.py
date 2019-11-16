from typing import List, Dict


def ensure_list(inst) -> List:
    """
    Wraps scalars or string types as a list, or returns the iterable instance.
    """
    if isinstance(inst, list):
        return inst
    if isinstance(inst, tuple):
        return list(inst)
    return [inst]


def flatten(d, parent_key='', sep='-'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, Dict):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


def first_valid(data: Dict, *names: str):
    result = None
    for name in names:
        result = result or data.get(name)
    return result
