"""Setup configuration for EDA_UFMV"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="eda-ufmv",
    version="0.3.0",
    author="EDA_UFMV Team",
    author_email="support@eda-ufmv.org",
    description="Universal Verification Framework for FPGA/Prototype Verification",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/EdaerCoser/EDA_UFMV",
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
