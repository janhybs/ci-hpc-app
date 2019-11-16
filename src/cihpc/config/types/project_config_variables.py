from typing import List, Dict, Any, Iterable
import itertools

from cihpc.shared.utils.data_util import ensure_list


class IVariation(dict):
    def __init__(self):
        super().__init__()
        self.index: int = 0
        self.total: int = 0


class ProjectConfigVariables:
    @staticmethod
    def first(iterator):
        return next(iter(iterator))

    def __init__(self, data: List[Dict[str, List[Dict[str, List]]]]):
        self.variations: List[Dict[str, Any]] = list()

        for section in data:
            section_type = self.first(section.keys())
            section_data = self.first(section.values())

            if section_type == 'matrix':
                values = [ensure_list(self.first(x.values())) for x in section_data]
                names = [self.first(x.keys()) for x in section_data]
                product = list(dict(zip(names, x)) for x in itertools.product(*values))
                self.variations.extend(product)

        if not self.variations:
            self.variations.append({})

    def loop(self) -> Iterable[IVariation]:
        total = len(self.variations)
        for index, variation in enumerate(self.variations):
            yield dict(total=total, index=index, **variation)

    def __call__(self, *args, **kwargs):
        return self.loop()