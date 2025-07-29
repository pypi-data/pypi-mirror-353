from setuptools import setup, find_packages
from pathlib import Path

# Safe reference to the current file's directory
this_directory = Path(__file__).resolve().parent
readme_path = this_directory / "README.md"
long_description = readme_path.read_text(encoding="utf-8")

setup(

    name="simplyRSA",
    version="1.51",
    description="Simple package for RSA analyses",
    author="Abraham Sanchez",
    author_email="abrahamss.av@gmail.com",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AbrahamSV/simplyRSA/',
    packages=["simplyRSA"]
)
