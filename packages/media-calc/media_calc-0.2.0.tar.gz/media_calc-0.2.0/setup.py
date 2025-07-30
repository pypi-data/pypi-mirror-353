import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding='utf-8')

VERSION = '0.2.0'  # Added new statistical functions
PACKAGE_NAME = 'media-calc'  # Changed to avoid conflicts with existing packages
AUTHOR = 'Omardev29'
AUTHOR_EMAIL = 'omaroficial365@gmail.com'

LICENSE = 'MIT'
DESCRIPTION = 'An efficient Python library for calculating the arithmetic mean of a list of numbers'
LONG_DESCRIPTION = README
LONG_DESC_TYPE = "text/markdown"

# Metadata adicional del proyecto
PROJECT_URLS = {
    'Source Code': 'https://github.com/Omardev29/media-calc',  # Reemplaza con tu URL de GitHub si tienes uno
    'Bug Tracker': 'https://github.com/Omardev29/media-calc/issues',
}

KEYWORDS = ['mathematics', 'statistics', 'average', 'mean', 'calculator']
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