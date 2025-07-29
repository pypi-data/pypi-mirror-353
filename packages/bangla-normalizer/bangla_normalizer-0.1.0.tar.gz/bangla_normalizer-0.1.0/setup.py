from setuptools import setup, find_packages
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

def get_version(package_name):
    with open(os.path.join(package_name, '__init__.py')) as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"').strip("'")
    return '0.1.0'

PACKAGE_NAME = "bangla_normalizer"

setup(
    name=PACKAGE_NAME,
    version=get_version(PACKAGE_NAME),
    author="Md. Shohanur Rahman",
    author_email="shorons38@gmail.com",
    description="A Python library for normalizing Bengali text.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/shohanur-shoron/bangla_normalizer.git",
    project_urls={
        "Bug Tracker": "https://github.com/shohanur-shoron/bangla_normalizer/issues",
    },
    license="MIT",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),

    install_requires=[
        "python-dateutil>=2.8.2",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Natural Language :: Bengali",
    ],
    python_requires=">=3.7",
    keywords="bengali, bangla, nlp, natural language processing, text normalization, text standardisation, bangla text processing, bengali text processing, text verbalization, spell-out, number to words, date to words, time to words, currency to words, taka normalization, percentage normalization, temperature normalization, ratio normalization, ordinal normalization, year normalization, phone number normalization, distance normalization, bangla nsw, bengali nsw, non-standard words, bangla tts, bengali tts, text to speech preprocessing, bangla unicode, bengali unicode, text cleaning, bangla data preprocessing, bengali data preprocessing, bangla text utilities, bengali text tools, bengali language, bangla language, indic nlp, bangla script, bengali script, text normalizer, bangla normalizer, bengali normalizer",
)