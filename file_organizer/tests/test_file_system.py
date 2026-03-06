"""
Tests for the OSFileSystem adapter.
Uses temporary directories to avoid touching the real file system.
"""

import pytest
from pathlib import Path
# from shutil import rmtree

from organizer.domain import FileItem, Directory
from organizer.infrastructure import OSFileSystem
from organizer.domain.exceptions import (
    SourceFileNotFoundError,
    # PermissionDeniedError,
    # DestinationExistsError,
    FileSystemError,
)


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def temp_dir(tmp_path) -> Path:
    """Create a clean temporary directory for each test."""
    return tmp_path


@pytest.fixture
def fs() -> OSFileSystem:
    """Provide an instance of OSFileSystem."""
    return OSFileSystem()


def create_test_files(base: Path, structure: dict) -> None:
    """
    Helper to create a directory structure from a dict.
    Example:
        {
            'file.txt': None,
            'sub': {
                'nested.txt': None,
                'empty': {}
            }
        }
    """
    for name, content in structure.items():
        path = base / name
        if content is None:  # file
            path.write_text('dummy content')
        elif isinstance(content, dict):  # directory
            path.mkdir()
            create_test_files(path, content)


# ----------------------------------------------------------------------
# Tests for scanning
# ----------------------------------------------------------------------


def test_scan_basic(temp_dir, fs):
    """Scan a simple directory with files and subdirectories."""
    structure = {
        'a.txt': None,
        'b.jpg': None,
        'sub': {
            'c.txt': None,
        },
    }
    create_test_files(temp_dir, structure)

    root = fs.scan(temp_dir, recursive=True)

    assert root.name == temp_dir.name
    assert len(root.children) == 3  # a.txt, b.jpg, sub

    # Check file items
    a_txt = root.get_child('a.txt')
    assert a_txt is not None
    assert isinstance(a_txt, FileItem)
    assert a_txt.name == 'a.txt'
    assert a_txt.suffix == '.txt'

    sub = root.get_child('sub')
    assert sub is not None
    assert isinstance(sub, Directory)
    assert len(sub.children) == 1
    c_txt = sub.get_child('c.txt')
    assert c_txt is not None


def test_scan_non_recursive(temp_dir, fs):
    """Scan without recursion – subdirectories are created but empty."""
    structure = {
        'a.txt': None,
        'sub': {
            'c.txt': None,
        },
    }
    create_test_files(temp_dir, structure)

    root = fs.scan(temp_dir, recursive=False)

    assert len(root.children) == 2
    sub = root.get_child('sub')
    assert sub is not None
    assert isinstance(sub, Directory)
    # sub should be empty because recursion was off
    assert len(sub.children) == 0


def test_scan_with_ignore_patterns(temp_dir, fs):
    """Files/directories matching ignore patterns are skipped."""
    structure = {
        'keep.txt': None,
        'ignore.tmp': None,
        'sub': {
            'also_ignore.log': None,
            'keep.md': None,
        },
    }
    create_test_files(temp_dir, structure)

    ignore = ['*.tmp', '*.log', 'sub']  # ignore the whole sub directory
    root = fs.scan(temp_dir, recursive=True, ignore_patterns=ignore)

    # keep.txt should be present
    assert root.get_child('keep.txt') is not None
    # ignore.tmp should be absent
    assert root.get_child('ignore.tmp') is None
    # sub directory should be absent (ignored by pattern 'sub')
    assert root.get_child('sub') is None


# ----------------------------------------------------------------------
# Tests for move
# ----------------------------------------------------------------------


def test_move_file(temp_dir, fs):
    """Move a file to a new location."""
    src = temp_dir / 'source.txt'
    src.write_text('data')
    dst_dir = temp_dir / 'dest'
    dst = dst_dir / 'source.txt'

    # Need a FileItem to move
    parent = Directory(temp_dir)
    file_item = FileItem(src, parent)

    fs.move(file_item, dst, Directory(dst_dir), dry_run=False)

    assert not src.exists()
    assert dst.exists()
    assert dst.read_text() == 'data'
    # Tree should be updated
    assert file_item.path == dst
    if file_item.parent is not None:
        assert file_item.parent.path == dst_dir


def test_move_with_conflict(temp_dir, fs):
    """If destination already exists, a new unique name is generated."""
    src = temp_dir / 'source.txt'
    src.write_text('data')
    dst_dir = temp_dir / 'dest'
    dst_dir.mkdir()
    existing = dst_dir / 'source.txt'
    existing.write_text('existing')

    parent = Directory(temp_dir)
    file_item = FileItem(src, parent)

    fs.move(file_item, existing, Directory(dst_dir), dry_run=False)

    assert not src.exists()
    # The existing file should remain untouched
    assert existing.read_text() == 'existing'
    # A new file with a suffix should have been created
    expected = dst_dir / 'source_(1).txt'
    assert expected.exists()
    assert expected.read_text() == 'data'
    assert file_item.path == expected


def test_move_nonexistent_source(temp_dir, fs):
    """Moving a file that does not exist raises SourceFileNotFoundError."""
    src = temp_dir / 'missing.txt'
    dst = temp_dir / 'dest' / 'missing.txt'
    parent = Directory(temp_dir)
    file_item = FileItem(src, parent)  # file_item exists but the physical file does not

    with pytest.raises(SourceFileNotFoundError):
        fs.move(file_item, dst, Directory(temp_dir / 'dest'), dry_run=False)


# ----------------------------------------------------------------------
# Tests for mkdir and rmdir
# ----------------------------------------------------------------------


def test_mkdir(temp_dir, fs):
    """Create a directory (and parents)."""
    path = temp_dir / 'a' / 'b' / 'c'
    fs.mkdir(path, parents=True)

    assert path.exists()
    assert path.is_dir()


def test_rmdir_empty(temp_dir, fs):
    """Remove an empty directory."""
    dir_path = temp_dir / 'empty'
    dir_path.mkdir()
    directory = Directory(dir_path)

    fs.rmdir(directory, dry_run=False)

    assert not dir_path.exists()
    # directory should be detached from its parent
    assert directory.parent is None


def test_rmdir_not_empty(temp_dir, fs):
    """Attempting to remove a non‑empty directory raises FileSystemError."""
    dir_path = temp_dir / 'not_empty'
    dir_path.mkdir()
    (dir_path / 'file.txt').write_text('data')
    directory = Directory(dir_path)

    with pytest.raises(FileSystemError, match='Directory not empty'):
        fs.rmdir(directory, dry_run=False)

    assert dir_path.exists()  # still there


# ----------------------------------------------------------------------
# Tests for dry run
# ----------------------------------------------------------------------


def test_dry_run_move(temp_dir, fs):
    """In dry run mode, files are not moved, tree is not updated."""
    src = temp_dir / 'source.txt'
    src.write_text('data')
    dst_dir = temp_dir / 'dest'
    dst = dst_dir / 'source.txt'

    parent = Directory(temp_dir)
    file_item = FileItem(src, parent)

    fs.move(file_item, dst, Directory(dst_dir), dry_run=True)

    # File should still be in the original location
    assert src.exists()
    assert not dst.exists()
    # Tree should be unchanged
    assert file_item.path == src
    assert file_item.parent == parent


def test_dry_run_rmdir(temp_dir, fs):
    """In dry run mode, directories are not removed physically, but are they detached from the tree?"""
    dir_path = temp_dir / 'empty'
    dir_path.mkdir()
    parent = Directory(temp_dir)
    directory = Directory(dir_path, parent)  # parent automatically adds it

    fs.rmdir(directory, dry_run=True)

    # Directory should still exist on disk
    assert dir_path.exists()
    # Depending on implementation, the tree may be updated. Currently it is not (see code).
    # We assume the tree remains unchanged.
    assert directory.parent is not None  # still attached
