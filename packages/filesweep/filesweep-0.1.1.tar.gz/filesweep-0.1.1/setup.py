import os
from setuptools import setup, find_packages

# Read version from version.txt
version_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), "version.txt")
try:
    with open(version_file, "r", encoding="utf-8") as f:
        version = f.read().strip()
        # Remove file path comment if present
        if version.startswith("//"):
            version = version.split("\n", 1)[1].strip()
except FileNotFoundError:
    print("Warning: version.txt not found. Using default version 0.1.0")
    version = "0.1.0"

# Read long description from README.md
with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='filesweep',
    version=version,
    packages=find_packages(),
    url='https://github.com/rakshithkalmadi/FileSweep',
    license='MIT',
    author='Rakshith Kalmadi',
    author_email='rakshithkalmadi@gmail.com',
    description='A tool for managing and organizing files in a directory',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Utilities',
    ],
    keywords='file management, file organization, cleanup, file scanner',
    project_urls={
        'Bug Reports': 'https://github.com/rakshithkalmadi/FileSweep/issues',
        'Source': 'https://github.com/rakshithkalmadi/FileSweep',
    },
    entry_points={
        'console_scripts': [
            'filesweep=filesweep:main',
        ],
    },
)
