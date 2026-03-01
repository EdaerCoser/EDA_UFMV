"""Setup configuration for sv_randomizer"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sv-randomizer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="SystemVerilog-style random constraint solver for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sv-randomizer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        # 核心功能无外部依赖
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "z3": [
            "z3-solver>=4.12.0",
        ],
        "stat": [
            "numpy>=1.21.0",
            "scipy>=1.7.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sv-rand=sv_randomizer.cli:main",
        ],
    },
)
