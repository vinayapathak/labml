from typing import Dict

import numpy as np

from ..colors import Text
from ..indicators import Indicator


class Writer:
    def write(self, *,
              global_step: int,
              indicators: Dict[str, Indicator]):
        raise NotImplementedError()


class ScreenWriter(Writer):
    def __init__(self):
        super().__init__()

        self._estimates = {}
        self._beta = 0.9
        self._beta_pow = {}
        self._last_printed_value = {}

    def update_estimate(self, k, v):
        if k not in self._estimates:
            self._estimates[k] = 0
            self._beta_pow[k] = 1.

        self._estimates[k] *= self._beta
        self._estimates[k] += (1 - self._beta) * v
        self._beta_pow[k] *= self._beta

    def get_empty_string(self, length, decimals):
        return ' ' * (length - 2 - decimals) + '-.' + '-' * decimals

    def get_value_string(self, k, v):
        if k not in self._estimates:
            assert v is None
            return self.get_empty_string(8, 2)

        estimate = self._estimates[k] / (1 - self._beta_pow[k])
        if abs(estimate) < 1e-9:
            lg = 0
        else:
            lg = int(np.ceil(np.log10(estimate))) + 1

        decimals = 7 - lg
        decimals = max(1, decimals)
        decimals = min(6, decimals)

        fmt = "{v:8,." + str(decimals) + "f}"
        if v is None:
            return self.get_empty_string(8, decimals)
        else:
            return fmt.format(v=v)

    def write(self, *,
              global_step: int,
              indicators: Dict[str, Indicator]):
        parts = []

        for ind in indicators.values():
            if not ind.is_print:
                continue

            parts.append((f" {ind.name}: ", None))

            if not ind.is_empty():
                v = ind.get_mean()
                self.update_estimate(ind.name, v)
                value = self.get_value_string(ind.name, v)
                self._last_printed_value[ind.name] = value
                parts.append((value, Text.value))
            elif ind.name in self._last_printed_value:
                value = self._last_printed_value[ind.name]
                parts.append((value, Text.subtle))
            else:
                value = self.get_value_string(ind.name, None)
                parts.append((value, Text.subtle))

        return parts
