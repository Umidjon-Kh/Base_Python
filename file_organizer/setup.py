#!/usr/bin/env python3
from setuptools import setup, find_packages

# Read the long description from README.md
with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    # Package name on PyPI (must be unique)
    name='file-organizer',
    # Version (follow Semantic Versioning: https://semver.org/)
    version='0.1.0',
    # Author details
    author='Umidjon-Kh',
    author_email='iexistedonlyforyou@gmail.com',
    # Short description (one line)
    description='Sort files into folders based on their extensions',
    # Long description from README
    long_description=long_description,
    long_description_content_type='text/markdown',
    # Project home page / repository URL
    url='https://github.com/Umidjon-kh/Base_Python.git/file_organizer',
    # Automatically find all packages (directories with __init__.py)
    packages=find_packages(),
    # Python version requirement
    python_requires='>=3.6',
    # External dependencies (none, only standard library)
    install_requires=[],
    # Entry point to create a command-line script
    entry_points={
        'console_scripts': [
            # After installation, 'organizer' command will call main() from organizer.cli
            'organizer = organizer.src.cli:main',
        ],
    },
    # Include non-code files specified in package_data
    include_package_data=True,
    # Additional files to include inside the package
    package_data={
        'organizer': [
            'organizer/config/default_rules.json',
            'organizer/loggers/logger.py',
            'organizer/configs/config.py',
        ],  # relative to package root
    },
    # Classifiers for PyPI (optional but recommended)
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
