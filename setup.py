"""Setup script for MetricMancer.

This file ensures compatibility with older build systems and GitHub Actions.
The primary configuration is in pyproject.toml.
"""

from setuptools import setup, find_packages

# Read version from pyproject.toml
VERSION = "3.1.0"

# Read dependencies from pyproject.toml
DEPENDENCIES = [
    "jinja2",
    "pytest",
    "pytest-cov",
    "coverage",
    "pydriller",
    "tqdm",
    "PyYAML",
    "autopep8",
    "flake8",
    "pip-licenses"
]

setup(
    name="metricmancer",
    version=VERSION,
    description="Multi-language software analytics tool for code quality, maintainability, and technical risk.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Thomas Lindqvist",
    author_email="fixaren54_eon@icloud.com",
    url="https://github.com/CmdrPrompt/MetricMancer",
    license="MIT",
    packages=find_packages(include=["src", "src.*"]),
    install_requires=DEPENDENCIES,
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={
        "console_scripts": [
            "metricmancer=src.main:main",
        ],
    },
)
