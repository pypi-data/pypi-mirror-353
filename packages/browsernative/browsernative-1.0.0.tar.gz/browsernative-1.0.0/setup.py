"""
Setup configuration for Browser Native Python Client
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
version = "1.0.0"
with open("browsernative/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]
            break

setup(
    name="browsernative",
    version=version,
    author="BNCA Team",
    author_email="support@monostate.ai",
    description="Lightning-fast web scraping Python SDK - 11x faster than traditional scrapers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/monostate/browsernative-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Text Processing :: Markup :: HTML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.900",
            "twine>=3.0",
        ],
    },
    keywords=[
        "web scraping",
        "browser automation", 
        "ai analysis",
        "screenshot",
        "pdf parsing",
        "data extraction",
        "web crawler",
        "html parser",
        "content extraction",
        "lightpanda",
        "puppeteer"
    ],
    project_urls={
        "Bug Reports": "https://github.com/monostate/browsernative-python/issues",
        "Source": "https://github.com/monostate/browsernative-python",
        "Documentation": "https://docs.bnca.dev",
    },
)