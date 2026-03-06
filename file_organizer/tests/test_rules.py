from pathlib import Path
from organizer.domain import FileItem, Directory, ExtensionRule, RuleSet

# Creating root folder for test
parent = Directory('/tmp')

# Creatin instances of FileItem
file1 = FileItem(Path('/tmp/document.txt'), parent)
file2 = FileItem(Path('/tmp/image.jpg'), parent)
file3 = FileItem(Path('/tmp/unknown.xyz'), parent)

# Creating rules
rule_txt = ExtensionRule(['.txt'], 'Documents')
rule_img = ExtensionRule(['.jpg', '.png'], 'Images')
rules = [rule_txt, rule_img]

# RuleSet с other_behavior = 'use_other'
rule_set = RuleSet(rules, other_behavior='use_other', ignore_extensions=['.bak'])

print(rule_set.get_target_folder(file1))  # Documents
print(rule_set.get_target_folder(file2))  # Images
print(rule_set.get_target_folder(file3))  # Other
