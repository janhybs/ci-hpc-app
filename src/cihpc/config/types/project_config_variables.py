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

    def __init__(self, data: List[Dict[str, List[Dict[str, List]]]], repetitions: int):
        self.variations: List[Dict[str, Any]] = list()
        self.repetitions = repetitions
        self.set_variables(data)

    def set_variables(self, new_variables: List[Dict[str, List[Dict[str, List]]]]):
        self.variations: List[Dict[str, Any]] = list()

        for section in new_variables:
            section_type: str = self.first(section.keys())
            section_data: Dict = self.first(section.values())

            if section_type == 'matrix':
                values = [ensure_list(self.first(x.values())) for x in section_data] + [list(range(self.repetitions))]
                names = [self.first(x.keys()) for x in section_data] + ["reps"]

                product = list(dict(zip(names, x)) for x in itertools.product(*values))
                self.variations.extend(product)

        if not self.variations:
            self.variations.append({})

    def loop(self) -> Iterable[IVariation]:
        total = len(self.variations)
        for index, variation in enumerate(self.variations):
            yield dict(total=total, index=index, **variation)

    def __len__(self):
        return len(self.variations)

    def __call__(self, *args, **kwargs):
        return self.loop()