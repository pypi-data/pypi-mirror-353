from setuptools import setup, find_packages
import os

# Read README.md content
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="biearce_time",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Your Name",
    author_email="your.email@example.com",
    description="A package that provides a static 'today' timestamp and time functions based on it.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/biearce_time",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 