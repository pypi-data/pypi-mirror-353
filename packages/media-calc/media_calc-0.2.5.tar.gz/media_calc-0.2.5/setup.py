import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

try:
    README = (HERE / "README.md").read_text(encoding='utf-8')
except:
    README = """
# media-calc

A comprehensive Python library for statistical calculations.

## Features

- Calculate arithmetic mean (media)
- Find median value (median)
- Get most frequent value (mode)
- Calculate variance (variance)
- Compute standard deviation (standard_deviation)

## Installation

```bash
pip install media-calc
```

## Quick Start

```python
from media import media, median, mode, variance, standard_deviation

numbers = [2, 4, 4, 4, 5, 5, 7, 9]
print(f"Mean: {media(numbers)}")              # 5.0
print(f"Median: {median(numbers)}")           # 4.5
print(f"Mode: {mode(numbers)}")               # 4
print(f"Variance: {variance(numbers)}")       # 4.0
print(f"Std Dev: {standard_deviation(numbers)}") # 2.0
```

For more information visit: https://github.com/omardev29/media-calc
"""

VERSION = '0.2.5'  # Added comprehensive test script and verified security
PACKAGE_NAME = 'media-calc'
AUTHOR = 'Omardev29'
AUTHOR_EMAIL = 'omaroficial365@gmail.com'

LICENSE = 'MIT'
DESCRIPTION = 'A comprehensive Python library for statistical calculations including mean, median, mode, variance, and standard deviation'
LONG_DESCRIPTION = README
LONG_DESC_TYPE = "text/markdown"

# Metadata adicional del proyecto
PROJECT_URLS = {
    'Source Code': 'https://github.com/omardev29/media-calc',
}

KEYWORDS = [
    'mathematics',
    'statistics',
    'average',
    'mean',
    'calculator',
    'median',
    'mode',
    'variance',
    'standard deviation',
    'data analysis'
]
CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
]

INSTALL_REQUIRES = [
    # No dependencies required for this simple package
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENSE,
    packages=find_packages(),
    install_requires=INSTALL_REQUIRES,
    include_package_data=True,
    keywords=KEYWORDS,
    project_urls=PROJECT_URLS,
    classifiers=CLASSIFIERS,
    python_requires='>=3.6'
)