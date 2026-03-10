"""
Tests for the rule repository implementations.
"""

import pytest
import json
from pathlib import Path

from organizer.domain import (
    FileItem,
    Directory,
)

from organizer.exceptions import (
    RuleNotFoundError,
    RuleFileNotFoundError,
    RuleFormatError,
    # UnknownBehaviorType,
)
from organizer.infrastructure.rules import JsonRuleRepository, InMemoryRuleRepository


# ----------------------------------------------------------------------
# Fixtures
# ----------------------------------------------------------------------


@pytest.fixture
def parent_dir() -> Directory:
    """Create a parent directory for FileItem objects."""
    return Directory('/tmp')


@pytest.fixture
def sample_rules_dict() -> dict:
    """Provide a sample rules dictionary for testing."""
    return {
        'other_behavior': 'use_other',
        'ignore_extensions': ['.bak'],
        'ignore_size_more_than': 10_000_000,  # 10 MB
        'ignore_size_less_than': 100,  # 100 bytes
        'rules': [
            {'type': 'extension', 'extensions': ['.txt', '.md'], 'folder': 'Documents', 'priority': 0},
            {'type': 'extension', 'extensions': ['.jpg', '.png'], 'folder': 'Images', 'priority': 0},
            {'type': 'size', 'min': 1024, 'max': 10240, 'folder': 'MediumFiles', 'priority': 50},
            {
                'type': 'composite',
                'operator': 'AND',
                'priority': 100,
                'rules': [
                    {'type': 'extension', 'extensions': ['.sh', '.bash'], 'folder': 'Scripts'},
                    {'type': 'size', 'min': 1024, 'max': 10240, 'folder': 'MediumFiles'},
                ],
            },
        ],
    }


# ----------------------------------------------------------------------
# Tests for InMemoryRuleRepository
# ----------------------------------------------------------------------


def test_in_memory_basic_loading(sample_rules_dict, parent_dir):
    """
    Test that the repository correctly loads simple extension rules.
    """
    repo = InMemoryRuleRepository(sample_rules_dict)
    rule_set = repo.load_rules()

    txt_file = FileItem(Path('/tmp/doc.txt'), parent_dir)
    jpg_file = FileItem(Path('/tmp/image.jpg'), parent_dir)
    unknown_file = FileItem(Path('/tmp/unknown.xyz'), parent_dir)

    assert rule_set.get_folder_name(txt_file) == 'Documents'
    assert rule_set.get_folder_name(jpg_file) == 'Images'
    assert rule_set.get_folder_name(unknown_file) == 'Other'


def test_in_memory_ignore_by_extension(sample_rules_dict, parent_dir):
    """
    Test that files with ignored extensions are skipped (return None).
    """
    repo = InMemoryRuleRepository(sample_rules_dict)
    rule_set = repo.load_rules()

    bak_file = FileItem(Path('/tmp/backup.bak'), parent_dir)
    assert rule_set.get_folder_name(bak_file) is None


def test_in_memory_ignore_by_size(sample_rules_dict, parent_dir):
    """
    Test that files outside the allowed size range are ignored.
    """
    repo = InMemoryRuleRepository(sample_rules_dict)
    rule_set = repo.load_rules()

    # File smaller than ignore_size_less_than
    small_file = FileItem(Path('/tmp/small.txt'), parent_dir)
    # Override the size because FileItem normally reads it from the real FS
    object.__setattr__(small_file, '_size', 50)
    object.__setattr__(small_file, '_size_fetched', True)
    assert rule_set.get_folder_name(small_file) is None

    # File larger than ignore_size_more_than
    huge_file = FileItem(Path('/tmp/huge.mov'), parent_dir)
    object.__setattr__(huge_file, '_size', 20_000_000)
    object.__setattr__(huge_file, '_size_fetched', True)
    assert rule_set.get_folder_name(huge_file) is None


def test_in_memory_priority(sample_rules_dict, parent_dir):
    """
    Test that rules with higher priority are evaluated first.
    We add a simple extension rule for .sh with low priority; the composite
    (priority 100) should still match first because it has higher priority.
    """
    # Add a low‑priority extension rule for .sh
    rules_dict = sample_rules_dict.copy()
    rules_dict['rules'].append(
        {
            'type': 'extension',
            'extensions': ['.sh'],
            'folder': 'ShellScripts',
            'priority': 10,  # lower than composite's 100
        }
    )

    repo = InMemoryRuleRepository(rules_dict)
    rule_set = repo.load_rules()

    # A script that meets both extension and size criteria
    script_file = FileItem(Path('/tmp/script.sh'), parent_dir)
    object.__setattr__(script_file, '_size', 5000)
    object.__setattr__(script_file, '_size_fetched', True)

    # Composite should win because of higher priority
    assert rule_set.get_folder_name(script_file) == 'MediumFiles/Scripts'


def test_in_memory_composite_and(sample_rules_dict, parent_dir):
    """
    Test that a composite rule with AND works correctly.
    """
    repo = InMemoryRuleRepository(sample_rules_dict)
    rule_set = repo.load_rules()

    # File that matches both sub‑rules
    good_script = FileItem(Path('/tmp/deploy.sh'), parent_dir)
    object.__setattr__(good_script, '_size', 5000)
    object.__setattr__(good_script, '_size_fetched', True)

    assert rule_set.get_folder_name(good_script) == 'MediumFiles/Scripts'

    # File with correct extension but wrong size – composite should not match
    wrong_size_script = FileItem(Path('/tmp/deploy.sh'), parent_dir)
    object.__setattr__(wrong_size_script, '_size', 50)
    object.__setattr__(wrong_size_script, '_size_fetched', True)
    # Falls through to other rules: size rule matches (priority 50)
    assert wrong_size_script.size == 50
    assert rule_set.get_folder_name(wrong_size_script) is None

    # File with correct size but wrong extension
    data_file = FileItem(Path('/tmp/data.bin'), parent_dir)
    object.__setattr__(data_file, '_size', 5000)
    object.__setattr__(data_file, '_size_fetched', True)
    # Size rule matches
    assert rule_set.get_folder_name(data_file) == 'MediumFiles'


def test_in_memory_other_behavior_raise(sample_rules_dict, parent_dir):
    """
    Test that when other_behavior = 'raise', an unmatched file raises RuleNotFoundError.
    """
    rules_dict = sample_rules_dict.copy()
    rules_dict['other_behavior'] = 'raise'
    repo = InMemoryRuleRepository(rules_dict)
    rule_set = repo.load_rules()

    unknown_file = FileItem(Path('/tmp/unknown.xyz'), parent_dir)
    with pytest.raises(RuleNotFoundError):
        rule_set.get_folder_name(unknown_file)


def test_in_memory_other_behavior_ignore(sample_rules_dict, parent_dir):
    """
    Test that when other_behavior = 'ignore', an unmatched file returns None.
    """
    rules_dict = sample_rules_dict.copy()
    rules_dict['other_behavior'] = 'ignore'
    repo = InMemoryRuleRepository(rules_dict)
    rule_set = repo.load_rules()

    unknown_file = FileItem(Path('/tmp/unknown.xyz'), parent_dir)
    assert rule_set.get_folder_name(unknown_file) is None


def test_in_memory_combine_with_default(parent_dir):
    """
    Test that combining user rules with default rules works.
    User rules should override default settings, and rules from both sources
    are merged, with user rules placed first (higher effective priority).
    """
    # Default rules
    default_rules_dict = {
        'other_behavior': 'use_other',
        'ignore_extensions': [],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [{'type': 'extension', 'extensions': ['.txt'], 'folder': 'Texts', 'priority': 10}],
    }
    default_repo = InMemoryRuleRepository(default_rules_dict)

    # User rules
    user_rules_dict = {
        'other_behavior': 'raise',  # should override default
        'ignore_extensions': ['.bak'],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [{'type': 'extension', 'extensions': ['.py'], 'folder': 'PythonScripts', 'priority': 20}],
    }
    repo = InMemoryRuleRepository(user_rules_dict, default_repo, combine=True)
    rule_set = repo.load_rules()

    # Check that user's other_behavior took precedence
    assert rule_set.other_behavior == 'raise'

    # Check that both rules are present and sorted by priority
    py_file = FileItem(Path('/tmp/script.py'), parent_dir)
    txt_file = FileItem(Path('/tmp/doc.txt'), parent_dir)

    # .py has higher priority and should match first
    assert rule_set.get_folder_name(py_file) == 'PythonScripts'
    # .txt should still match
    assert rule_set.get_folder_name(txt_file) == 'Texts'


# ----------------------------------------------------------------------
# Tests for JsonRuleRepository
# ----------------------------------------------------------------------


def test_json_repository(tmp_path, parent_dir):
    """
    Test loading rules from a temporary JSON file.
    """
    json_data = {
        'other_behavior': 'use_other',
        'ignore_extensions': ['.bak'],
        'ignore_size_more_than': None,
        'ignore_size_less_than': None,
        'rules': [{'type': 'extension', 'extensions': ['.txt'], 'folder': 'Documents'}],
    }
    json_file = tmp_path / 'rules.json'
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_data, f)

    repo = JsonRuleRepository(json_file)
    rule_set = repo.load_rules()

    txt_file = FileItem(Path('/tmp/doc.txt'), parent_dir)
    assert rule_set.get_folder_name(txt_file) == 'Documents'
    unknown_file = FileItem(Path('/tmp/unknown.xyz'), parent_dir)
    assert rule_set.get_folder_name(unknown_file) == 'Other'


def test_json_repository_missing_file(tmp_path):
    """Test that loading from a non‑existent file raises RuleFileNotFoundError."""
    non_existent = tmp_path / 'no_such_file.json'
    repo = JsonRuleRepository(non_existent)
    with pytest.raises(RuleFileNotFoundError):
        repo.load_rules()


def test_json_repository_invalid_json(tmp_path):
    """Test that invalid JSON raises RuleFormatError."""
    json_file = tmp_path / 'bad.json'
    with open(json_file, 'w') as f:
        f.write('{ this is not json }')
    repo = JsonRuleRepository(json_file)
    with pytest.raises(RuleFormatError):
        repo.load_rules()
