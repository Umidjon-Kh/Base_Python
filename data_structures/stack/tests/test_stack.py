import pytest
from ..stack import Stack


# Fixtures to get filled stack and empty stack
@pytest.fixture
def filled_stack() -> Stack:
    return Stack(['item', 1, 3, 4, 5, ['another', 'list', ['nested', 'list']], '6', 7])


@pytest.fixture
def empty_stack() -> Stack:
    return Stack()


# Tests
def test_stack_creating(empty_stack) -> None:
    # Only chacking stack when creating none or not and bool
    assert empty_stack is not None


def test_stack_push(empty_stack) -> None:
    empty_stack.push(1)
    empty_stack.push('1')

    # Check stack have 1 and '1' or not
    assert '1' in empty_stack
    assert 1 in empty_stack


def test_stack_pop(filled_stack) -> None:
    # Checking stack pop method correct work
    assert filled_stack.pop() == 7
    assert filled_stack.pop() == '6'
    assert isinstance(filled_stack.pop(), list)


def test_pop_empty_stack(empty_stack) -> None:
    with pytest.raises(IndexError):
        empty_stack.pop()


def test_stack_peek(filled_stack) -> None:
    # Checking stack peek method properly work
    copy_stack = filled_stack.copy()
    assert filled_stack.peek() == 7
    assert filled_stack.peek() == 7
    assert filled_stack.copy() == copy_stack


def test_stack_set_and_get(filled_stack) -> None:
    # Checking dunder method set item properly work
    filled_stack[1] = '7'
    filled_stack[5] = ['hello', 'world']

    # Checking dunder method get item properly work
    assert filled_stack[1] == '7'
    assert isinstance(filled_stack[5], list)


def test_get_item_type_err(filled_stack) -> None:
    with pytest.raises(TypeError):
        filled_stack['hello']


def test_set_item_type_err(filled_stack) -> None:
    with pytest.raises(TypeError):
        filled_stack['hello'] = 'error'


def test_index_error_filled(empty_stack, filled_stack) -> None:
    with pytest.raises(IndexError):
        filled_stack[99] = 'error'


def test_index_error_empty(empty_stack) -> None:
    with pytest.raises(IndexError):
        empty_stack[-1] = 'error'


def test_stack_slice_method(filled_stack) -> None:
    # Checking stack slicing method properly work
    sliced = filled_stack[1::2]
    lst_copy_slice = filled_stack.copy()[1::2]

    assert sliced == [1, 4, ['another', 'list', ['nested', 'list']], 7]
    assert sliced == lst_copy_slice


def test_stack_bool_method(empty_stack, filled_stack) -> None:
    # Checking dunder bool method of stack cls
    assert bool(empty_stack) is False
    assert bool(filled_stack) is True


def test_stack_len_method(empty_stack, filled_stack) -> None:
    # Checking stack dunder method len
    assert len(empty_stack) == 0
    assert len(filled_stack) != 0


def test_stack_iteration(filled_stack) -> None:
    # Checking that iterating method woroks properly
    copy_stack = filled_stack.copy()

    for item in filled_stack:
        pass

    assert copy_stack == filled_stack.copy()


def test_stack_reversed(filled_stack) -> None:
    # Checking reversed lazy load iteration woroks or not
    assert list(reversed(filled_stack)) == list(reversed(filled_stack.copy()))
