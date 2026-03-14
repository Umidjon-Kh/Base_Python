from dataclasses import dataclass, field
from typing import Optional, Any, Generator
from .node import Node


@dataclass
class Stack:
    _top: Optional[Node] = field(default=None, repr=False)
    _size: int = field(init=False, default=0)

    def push(self, value: Any) -> None:
        """Creates new node with any type value"""
        new_node = Node(value)
        new_node.next = self._top
        self._top = new_node
        self._size += 1

    def pop(self) -> Any:
        """Removes Last in element from Stack"""
        if self._top is None:
            raise IndexError('Stack is empty')

        removed = self._top
        self._top = self._top.next
        self._size -= 1
        return removed.value

    def peek(self) -> Any:
        """Shows last in element in stack"""
        if self._top is None:
            raise IndexError('Stack is empty')
        return self._top.value

    def copy(self) -> 'Stack':
        """Returns a copy of stack that not connected to this stack"""
        temp = Stack()
        new_stack = Stack()

        current = self._top

        while current:
            temp.push(current.value)
            current = current.next

        while temp._top is not None:
            value = temp.pop()
            new_stack.push(value)

        return new_stack

    def __len__(self) -> int:
        """Returns size for Stack"""
        return self._size

    def __iter__(self) -> Generator[Any, None, None]:
        """For iterating object stack"""
        current = self._top
        while current:
            yield current.value
            current = current.next

    def __contains__(self, item) -> bool:
        """Checks stack for contains item or not"""
        current = self._top
        while current:
            if current.value == item:
                return True
            current = current.next
        return False

    def __bool__(self) -> bool:
        """Returns true if stack is not None"""
        return self._top is not None

    def __str__(self) -> str:
        """String method shows all stack values in user frinedly output"""
        values = []
        current = self._top

        while current:
            values.append(current.value)
            current = current.next

        return 'Stack(top -> ' + ' -> '.join(map(str, values)) + ')'
