from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass(slots=True)
class Node:
    _value: Any
    _next: Optional['Node'] = field(init=False, default=None)

    @property
    def value(self) -> Any:
        return self._value

    @property
    def next(self) -> Any:
        return self._next

    @next.setter
    def next(self, value: Optional['Node']) -> None:
        self._next = value
