from setuptools import setup, find_packages

setup(
    # Package identification
    # Unique name of file organizer from svedish klat
    name='klart',
    # Version of package
    version='1.0.3',
    # Simple mini description of file organizer
    description='Organize files into folders based on configurable rules',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    # Long description not in rst, only in markdown.
    # Author
    author='Umidjon Khodjaev',
    # Email
    author_email='iexistedonlyforyou@gmail.com',
    # Licence: type Mit is free
    license='MIT',
    # Url for my github project code
    url='https://github.com/Umidjon-Kh/Base_Python/tree/main/klart',
    # What includes a package
    packages=find_packages(),
    # Reuirements package configs
    package_data={
        'organizer': ['data/*.json'],
    },
    # Production requirements for user
    install_requires=[
        'loguru>=0.7.0',
    ],
    # Extra requirements for developer
    extras_require={
        'dev': [
            'pytest>=7.0',
            'pytest-mock>=3.0',
        ],
    },
    # Cli command script runner
    entry_points={
        'console_scripts': [
            'klart=organizer.interfaces.cli.main:main',
        ],
    },
    # Pip creates runner file organizer in system after pip install.
    # Format command=package.module:function
    # Pip runs this command when you class organizer
    # Pythonversion to use
    python_requires='>=3.12',
    # ── Классификаторы ────────────────────────────────────────────────────────
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 5 - Stable - stable working or you can write Production
        # 3 - Aplha, 4 - Beta
        'Environment :: Console',
        # For which type of users
        'Intended Audience :: End Users/Desktop',
        # License standart format for PyPi
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.12',
        'Topic :: Utilities',
    ],
)
