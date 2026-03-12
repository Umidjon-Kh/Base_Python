"""
Tests for OSFileSystem adapter.
Uses tmp_path to avoid touching the real file system.
"""

import pytest
from pathlib import Path

from ..domain import FileItem, Directory
from ..infrastructure import OSFileSystem
from ..exceptions import SourceFileNotFoundError


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def fs() -> OSFileSystem:
    return OSFileSystem()


def make_files(base: Path, names: list) -> None:
    """Create empty files with dummy content."""
    for name in names:
        (base / name).write_text('dummy')


def make_structure(base: Path, structure: dict) -> None:
    """Create nested files/dirs from a dict. None = file, dict = directory."""
    for name, content in structure.items():
        path = base / name
        if content is None:
            path.write_text('dummy')
        elif isinstance(content, dict):
            path.mkdir()
            make_structure(path, content)


# ── scan ──────────────────────────────────────────────────────────────────────


def test_scan_flat_directory(tmp_path, fs):
    """Flat scan returns correct number and types of children."""
    make_files(tmp_path, ['a.txt', 'b.jpg'])
    root = fs.scan(tmp_path, recursive=False)

    assert len(root.children) == 2
    assert root.get_child('a.txt') is not None
    assert root.get_child('b.jpg') is not None
    assert isinstance(root.get_child('a.txt'), FileItem)


def test_scan_recursive_walks_subdirs(tmp_path, fs):
    """Recursive scan finds files in all subdirectories."""
    make_structure(
        tmp_path,
        {
            'a.txt': None,
            'sub': {'b.txt': None, 'deep': {'c.txt': None}},
        },
    )
    root = fs.scan(tmp_path, recursive=True)
    files = list(root.walk_files())
    assert len(files) == 3


def test_scan_non_recursive_skips_subdir_files(tmp_path, fs):
    """Non-recursive scan does not include files inside subdirectories."""
    make_structure(tmp_path, {'a.txt': None, 'sub': {'b.txt': None}})
    root = fs.scan(tmp_path, recursive=False)
    files = list(root.walk_files())
    assert len(files) == 1
    assert files[0].name == 'a.txt'


def test_scan_ignore_patterns(tmp_path, fs):
    """Files matching ignore_patterns are excluded."""
    make_files(tmp_path, ['a.txt', 'b.log', 'c.bak'])
    root = fs.scan(tmp_path, recursive=False, ignore_patterns=['*.log', '*.bak'])
    files = list(root.walk_files())
    assert len(files) == 1
    assert files[0].name == 'a.txt'


def test_scan_empty_directory(tmp_path, fs):
    """Scanning an empty directory returns zero children."""
    root = fs.scan(tmp_path, recursive=False)
    assert len(root.children) == 0


def test_scan_builds_correct_tree_structure(tmp_path, fs):
    """Scanned tree has correct parent/child relationships."""
    make_structure(tmp_path, {'a.txt': None, 'sub': {'b.txt': None}})
    root = fs.scan(tmp_path, recursive=True)

    sub = root.get_child('sub')
    assert isinstance(sub, Directory)
    assert sub.get_child('b.txt') is not None


# ── move ──────────────────────────────────────────────────────────────────────


def test_move_physically_moves_file(tmp_path, fs):
    """File is moved from source to destination."""
    src = tmp_path / 'source'
    src.mkdir()
    (src / 'doc.txt').write_text('hello')

    dest = tmp_path / 'dest'
    dest.mkdir()

    root = fs.scan(src, recursive=False)
    file_item = list(root.walk_files())[0]
    new_parent = Directory(dest)

    fs.move(file_item=file_item, destination=dest / 'doc.txt', new_parent=new_parent, dry_run=False)

    assert (dest / 'doc.txt').exists()
    assert not (src / 'doc.txt').exists()


def test_move_dry_run_leaves_file_in_place(tmp_path, fs):
    """dry_run=True does not physically move the file."""
    src = tmp_path / 'source'
    src.mkdir()
    (src / 'doc.txt').write_text('hello')

    dest = tmp_path / 'dest'
    dest.mkdir()

    root = fs.scan(src, recursive=False)
    file_item = list(root.walk_files())[0]
    new_parent = Directory(dest)

    fs.move(file_item=file_item, destination=dest / 'doc.txt', new_parent=new_parent, dry_run=True)

    assert (src / 'doc.txt').exists()  # still in source
    assert not (dest / 'doc.txt').exists()  # not in dest


def test_move_missing_source_raises(tmp_path, fs):
    """Moving a file that doesn't exist raises SourceFileNotFoundError."""
    parent = Directory(tmp_path)
    ghost = FileItem(tmp_path / 'ghost.txt', parent)
    dest_dir = tmp_path / 'dest'
    dest_dir.mkdir()

    with pytest.raises(SourceFileNotFoundError):
        fs.move(file_item=ghost, destination=dest_dir / 'ghost.txt', new_parent=Directory(dest_dir), dry_run=False)


def test_move_resolves_name_conflict(tmp_path, fs):
    """If destination file already exists, a unique name is generated."""
    src = tmp_path / 'source'
    src.mkdir()
    (src / 'doc.txt').write_text('new')

    dest = tmp_path / 'dest'
    dest.mkdir()
    (dest / 'doc.txt').write_text('existing')  # conflict!

    root = fs.scan(src, recursive=False)
    file_item = list(root.walk_files())[0]
    new_parent = Directory(dest)

    fs.move(file_item=file_item, destination=dest / 'doc.txt', new_parent=new_parent, dry_run=False)

    assert (dest / 'doc.txt').exists()  # original untouched
    assert (dest / 'doc_(1).txt').exists()  # moved with new name


def test_move_creates_dest_parent_dirs(tmp_path, fs):
    """move() creates destination parent directories if they don't exist."""
    src = tmp_path / 'source'
    src.mkdir()
    (src / 'doc.txt').write_text('hello')

    deep_dest = tmp_path / 'a' / 'b' / 'c' / 'doc.txt'

    root = fs.scan(src, recursive=False)
    file_item = list(root.walk_files())[0]

    fs.move(file_item=file_item, destination=deep_dest, new_parent=Directory(deep_dest.parent), dry_run=False)

    assert deep_dest.exists()


# ── mkdir ─────────────────────────────────────────────────────────────────────


def test_mkdir_creates_nested_dirs(tmp_path, fs):
    """mkdir with parents=True creates all missing intermediate directories."""
    target = tmp_path / 'a' / 'b' / 'c'
    fs.mkdir(target)
    assert target.exists() and target.is_dir()


def test_mkdir_on_existing_dir_no_error(tmp_path, fs):
    """mkdir on an already existing directory does not raise."""
    target = tmp_path / 'existing'
    target.mkdir()
    fs.mkdir(target)  # should not raise
