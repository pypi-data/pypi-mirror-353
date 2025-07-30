"""
Setup script for Przelewy24 Python SDK
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    raise FileNotFoundError(
        "requirements.txt file is missing. This file is required for proper dependency management. "
        "Please ensure requirements.txt exists in the project root."
    )

setup(
    name="przelewy24-python",
    version="1.0.0",
    author="Dawid Iwański",
    author_email="d.iwanski@secc.me",
    description="Python SDK for Przelewy24 payment gateway",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ItsRaelx/PythonPrzelewy24",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Point-Of-Sale",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="przelewy24 payment gateway api sdk",
    project_urls={
        "Bug Reports": "https://github.com/ItsRaelx/PythonPrzelewy24/issues",
        "Source": "https://github.com/ItsRaelx/PythonPrzelewy24",
        "Documentation": "https://github.com/ItsRaelx/PythonPrzelewy24",
    },
) 