import pytest
from stack import Stack


# ------ Fixtures ---------
@pytest.fixture
def filled_stack() -> Stack:
    stack = Stack()
    for n in range(10):
        stack.push(n)
    return stack


@pytest.fixture
def empty_stack() -> Stack:
    return Stack()


# ------- Tests ----------
def test_stack_creation(empty_stack, filled_stack) -> None:
    # Checking dunder bool method of stuck and stacks properly creation
    assert bool(empty_stack) is False
    assert bool(filled_stack) is True


def test_stack_len_method(empty_stack, filled_stack) -> None:
    # Checking properly work of dunder len method
    assert len(empty_stack) == 0
    assert len(filled_stack) == 10


def test_stack_push_method(empty_stack, filled_stack) -> None:
    # Checking stack push method that adds new node to stack
    empty_stack.push(1)
    filled_stack.push(1)

    assert len(empty_stack) == 1
    assert len(filled_stack) == 11


def test_stack_pop_method(filled_stack) -> None:
    # Checking stack pop method work
    assert filled_stack.pop() == 9


def test_stack_pop_index_err(empty_stack) -> None:
    # Checking stack raises Indexerror for empty stack ot not
    with pytest.raises(IndexError):
        empty_stack.pop()


def test_stack_peek_method(filled_stack) -> None:
    # Checking stack peek method
    filled_stack.push(15)
    assert filled_stack.peek() == 15


def test_stack_peek_index_err(empty_stack) -> None:
    # Checking stack raises IndexError for empty stack or not
    with pytest.raises(IndexError):
        empty_stack.peek()


def test_stack_copy_method(filled_stack) -> None:
    copied_stack = filled_stack.copy()

    assert copied_stack is not filled_stack
    assert copied_stack == filled_stack


def test_stack_iter_method(filled_stack) -> None:
    for node in filled_stack:
        assert node == filled_stack.pop()


def test_stack_contain_method(filled_stack, empty_stack) -> None:
    # Checking stack contain method
    assert 7 in filled_stack
    assert 3 not in empty_stack


def test_stack_str_method(filled_stack) -> None:
    assert str(filled_stack).startswith('Stack(top')
