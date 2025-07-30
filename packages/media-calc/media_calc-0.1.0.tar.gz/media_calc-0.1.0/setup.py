import pathlib
from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding='utf-8')

VERSION = '0.1.0'
PACKAGE_NAME = 'media-calc'  # Changed to avoid conflicts with existing packages
AUTHOR = 'Omardev29'
AUTHOR_EMAIL = 'omaroficial365@gmail.com'

LICENSE = 'MIT'
DESCRIPTION = 'A simple library to calculate the average of a list of numbers'
LONG_DESCRIPTION = README
LONG_DESC_TYPE = "text/markdown"

INSTALL_REQUIRES = [
    # No dependencies required for this simple package
]

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description_content_type=LONG_DESC_TYPE,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    install_requires=INSTALL_REQUIRES,
    license=LICENSE,
    packages=find_packages(),
    include_package_data=True
)