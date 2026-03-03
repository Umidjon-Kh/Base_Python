#!/usr/bin/env python3
"""
Setup script for File Organizer package.
This script installs the 'organizer' package and makes the CLI command available.
"""

from setuptools import setup, find_packages  # type: ignore

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    # Package name on PyPI (must be unique)
    name="file-organizer",
    # Version (follow Semantic Versioning)
    version="0.3.0",
    # Author details
    author="Umidjon-Kh",
    author_email="iexistedonlyforyou@gmail.com",
    # Short description (one line)
    description="Sort files into folders based on their extensions",
    # Long description from README
    long_description=long_description,
    long_description_content_type="text/markdown",
    # Project home page / repository URL
    url="https://github.com/Umidjon-kh/Base_Python/tree/main/refactoring",
    # Automatically find all packages (directories with __init__.py)
    packages=find_packages(),
    # Python version requirement
    python_requires=">=3.6",
    # External dependencies
    install_requires=[
        "loguru",
    ],
    # Entry point to create a command-line script
    entry_points={
        "console_scripts": [
            # After installation, 'organizer' command will call main() from organizer.src.cli
            "organizer = organizer.src.cli:main",
        ],
    },
    # Include non-code files specified in MANIFEST.in
    include_package_data=True,
    # Additional classifiers for PyPI (optional)
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
        "Environment :: Console",
    ],
    # Project license
    license="MIT",
)
