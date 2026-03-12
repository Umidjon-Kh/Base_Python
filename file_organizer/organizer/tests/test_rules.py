"""
Tests for rule repository implementations and RuleSet behavior.
"""

import pytest
import json
from pathlib import Path

from organizer.domain import FileItem, Directory
from organizer.exceptions import (
    RuleNotFoundError,
    RuleFileNotFoundError,
    RuleFormatError,
    # RuleValidationError,
)
from organizer.infrastructure.rules import JsonRuleRepository, InMemoryRuleRepository


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def parent_dir() -> Directory:
    return Directory('/tmp')


@pytest.fixture
def sample_rules_cfg() -> dict:
    """Rules dict — same structure as a rules JSON file."""
    return {
        'other_behavior': 'use_other',
        'ignore_extensions': ['.bak'],
        'ignore_size_more_than': 10_000_000,  # 10 MB
        'ignore_size_less_than': None,
        'rules': [
            {'type': 'extension', 'extensions': ['.txt', '.md'], 'folder': 'Documents', 'priority': 0},
            {'type': 'extension', 'extensions': ['.jpg', '.png'], 'folder': 'Images', 'priority': 0},
            {'type': 'size', 'min': 1024, 'max': 10240, 'folder': 'MediumFiles', 'priority': 50},
            {
                'type': 'composite',
                'operator': 'AND',
                'priority': 100,
                'rules': [
                    {'type': 'extension', 'extensions': ['.sh'], 'folder': 'Scripts'},
                    {'type': 'size', 'min': 1024, 'max': 10240, 'folder': 'MediumFiles'},
                ],
            },
        ],
    }


@pytest.fixture
def rules_file(tmp_path, sample_rules_cfg) -> Path:
    """Write sample_rules_cfg to a temp JSON file."""
    path = tmp_path / 'rules.json'
    path.write_text(json.dumps(sample_rules_cfg))
    return path


@pytest.fixture
def default_repo(rules_file) -> JsonRuleRepository:
    return JsonRuleRepository(rules_file)


# ── JsonRuleRepository ────────────────────────────────────────────────────────


def test_json_repo_extension_rules(default_repo, parent_dir):
    """JsonRuleRepository correctly maps files via extension rules."""
    rule_set = default_repo.load_rules()

    txt = FileItem(Path('/tmp/doc.txt'), parent_dir)
    jpg = FileItem(Path('/tmp/img.jpg'), parent_dir)
    xyz = FileItem(Path('/tmp/unknown.xyz'), parent_dir)

    assert rule_set.get_folder_name(txt) == 'Documents'
    assert rule_set.get_folder_name(jpg) == 'Images'
    assert rule_set.get_folder_name(xyz) == 'Other'  # use_other behavior


def test_json_repo_missing_file_raises(tmp_path):
    """Non-existent file raises RuleFileNotFoundError."""
    repo = JsonRuleRepository(tmp_path / 'missing.json')
    with pytest.raises(RuleFileNotFoundError):
        repo.load_rules()


def test_json_repo_invalid_json_raises(tmp_path):
    """Corrupted JSON raises RuleFormatError."""
    path = tmp_path / 'bad.json'
    path.write_text('{ not valid }')
    repo = JsonRuleRepository(path)
    with pytest.raises(RuleFormatError):
        repo.load_rules()


def test_ruleset_ignore_extension(default_repo, parent_dir):
    """.bak files are always skipped regardless of other rules."""
    rule_set = default_repo.load_rules()
    bak = FileItem(Path('/tmp/file.bak'), parent_dir)
    assert rule_set.get_folder_name(bak) is None


def test_ruleset_ignore_size_more_than(default_repo, tmp_path, parent_dir):
    """Files exceeding ignore_size_more_than are skipped."""
    big = tmp_path / 'big.txt'
    big.write_bytes(b'x' * 10_000_001)
    rule_set = default_repo.load_rules()
    item = FileItem(big, parent_dir)
    assert rule_set.get_folder_name(item) is None


def test_ruleset_raise_behavior(tmp_path, parent_dir):
    """other_behavior='raise' raises RuleNotFoundError for unmatched files."""
    cfg = {
        'other_behavior': 'raise',
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [{'type': 'extension', 'extensions': ['.txt'], 'folder': 'Docs', 'priority': 0}],
    }
    path = tmp_path / 'rules.json'
    path.write_text(json.dumps(cfg))
    rule_set = JsonRuleRepository(path).load_rules()

    unknown = FileItem(Path('/tmp/file.xyz'), parent_dir)
    with pytest.raises(RuleNotFoundError):
        rule_set.get_folder_name(unknown)


def test_ruleset_ignore_behavior(tmp_path, parent_dir):
    """other_behavior='ignore' returns None for unmatched files."""
    cfg = {
        'other_behavior': 'ignore',
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [{'type': 'extension', 'extensions': ['.txt'], 'folder': 'Docs', 'priority': 0}],
    }
    path = tmp_path / 'rules.json'
    path.write_text(json.dumps(cfg))
    rule_set = JsonRuleRepository(path).load_rules()

    unknown = FileItem(Path('/tmp/file.xyz'), parent_dir)
    assert rule_set.get_folder_name(unknown) is None


# ── InMemoryRuleRepository ────────────────────────────────────────────────────


def test_in_memory_rules_cfg_no_combine(default_repo, parent_dir):
    """combine=False with rules_cfg: only user rules apply."""
    only_py = {
        'other_behavior': 'ignore',
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [
            {'type': 'extension', 'extensions': ['.py'], 'folder': 'Python', 'priority': 0},
        ],
    }
    repo = InMemoryRuleRepository(default_repo=default_repo, rules_cfg=only_py, combine=False)
    rule_set = repo.load_rules()

    py = FileItem(Path('/tmp/script.py'), parent_dir)
    txt = FileItem(Path('/tmp/doc.txt'), parent_dir)

    assert rule_set.get_folder_name(py) == 'Python'
    assert rule_set.get_folder_name(txt) is None  # default rules not active


def test_in_memory_rules_cfg_combine(default_repo, parent_dir):
    """combine=True: user rules_cfg added on top of default rules."""
    extra = {
        'other_behavior': 'use_other',
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [
            {'type': 'extension', 'extensions': ['.py'], 'folder': 'Python', 'priority': 10},
        ],
    }
    repo = InMemoryRuleRepository(default_repo=default_repo, rules_cfg=extra, combine=True)
    rule_set = repo.load_rules()

    # user rule works
    py = FileItem(Path('/tmp/script.py'), parent_dir)
    assert rule_set.get_folder_name(py) == 'Python'

    # default rules also work
    txt = FileItem(Path('/tmp/doc.txt'), parent_dir)
    assert rule_set.get_folder_name(txt) == 'Documents'


def test_in_memory_rules_repo_override(default_repo, tmp_path, parent_dir):
    """rules_repo replaces default rules when combine=False."""
    custom_cfg = {
        'other_behavior': 'ignore',
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [{'type': 'extension', 'extensions': ['.py'], 'folder': 'Python', 'priority': 0}],
    }
    custom_path = tmp_path / 'custom.json'
    custom_path.write_text(json.dumps(custom_cfg))
    custom_repo = JsonRuleRepository(custom_path)

    repo = InMemoryRuleRepository(default_repo=default_repo, rules_repo=custom_repo, combine=False)
    rule_set = repo.load_rules()

    py = FileItem(Path('/tmp/script.py'), parent_dir)
    txt = FileItem(Path('/tmp/doc.txt'), parent_dir)

    assert rule_set.get_folder_name(py) == 'Python'
    assert rule_set.get_folder_name(txt) is None


def test_in_memory_no_rules_cfg_no_combine_empty_rules(default_repo, parent_dir):
    """No rules_cfg and combine=False: empty rules list, other_behavior from default setter."""
    repo = InMemoryRuleRepository(default_repo=default_repo, combine=False)
    rule_set = repo.load_rules()

    # No rules → falls through to other_behavior which is 'use_other' from default
    txt = FileItem(Path('/tmp/doc.txt'), parent_dir)
    assert rule_set.get_folder_name(txt) == 'Other'
