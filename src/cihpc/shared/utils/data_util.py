from typing import List, Dict, Iterable


def distinct(items: Iterable, sort=True, reverse=True, key=None) -> List:
    unique_items = list(set(items))
    if sort:
        if key:
            return sorted(unique_items, key=key, reverse=reverse)
        else:
            return sorted(unique_items, key=key, reverse=reverse)
    return unique_items


unique = distinct


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


def first_valid(data: Dict, *names: str, default=None):
    for name in names:
        if name in data:
            return data[name]
    return default
