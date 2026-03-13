from dataclasses import dataclass, field
from typing import List, Any, Generator, Iterator


# Frozen works cause you dont change storage value
# You only change only list object not Stack attr, like Tuple "Immutabelity" :)
@dataclass(frozen=True, slots=True)
class Stack:
    _storage: List[Any] = field(default_factory=list)

    def push(self, item) -> None:
        """Appends storage list with item"""
        self._storage.append(item)

    def pop(self) -> Any:
        """Returns last item from storage and removes"""
        if not self.is_empty():
            return self._storage.pop()
        raise IndexError('Can\'t pop from empty stack')

    def peek(self) -> Any:
        """Returns last item in storage without removing"""
        return self._storage[-1] if self._storage else None

    def is_empty(self) -> bool:
        """Checks storage list empty or not"""
        return len(self._storage) == 0

    def __len__(self) -> int:
        """How many items in storage list"""
        return len(self._storage)

    def __bool__(self) -> bool:
        """
        Returns true if storage even if have only one item
        If not returns false
        """
        return bool(self._storage)

    def __str__(self) -> str:
        return f'{self._storage}'

    def copy(self) -> List[Any]:
        """Retruns copy of storage list"""
        return self._storage.copy()

    def __setitem__(self, index, value) -> None:
        """Sets new value for stack storage list item  like stack[0] = value"""
        if isinstance(index, int):
            if index >= len(self._storage) or index < -len(self._storage):
                raise IndexError('Stack index out of range')
            self._storage[index] = value
            return
        raise TypeError(f'Invalid index type {type(index).__name__}')

    def __getitem__(self, index) -> Any:
        """
        Method to get item in stack like stack[1]
        Suppoerts slice method raises IndexError if index out of range
        """
        # If index not slice only a index
        if isinstance(index, int):
            if index >= len(self._storage) or index < -len(self._storage):
                raise IndexError('Stack index out of range')
            return self._storage[index]

        if isinstance(index, slice):
            # If slice
            return self._storage[index]

        raise TypeError(f'Invalid index type {type(index).__name__}')

    def __contains__(self, item) -> bool:
        """Checks storage contains item or not"""
        return item in self._storage

    def __iter__(self) -> Generator[Any, None, None]:
        """Yields storage objects values one by one"""
        for item in self._storage.copy():
            yield item

    def __reversed__(self) -> Iterator[Any]:
        """Returns reversed stack storage list lazy_load iterator"""
        return reversed(self._storage)
