from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="alumathvanguard",
    version="1.0.0",
    author="ALU Math Vanguard Group 15",
    description="A fun matrix multiplication library with personality from Group 15",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/izabayo7/Formative2Group15/tree/main/Group15MatrixMultiplier",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Mathematics",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies needed for basic matrix operations
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    keywords="matrix multiplication linear algebra education ALU",
    project_urls={
        "Bug Reports": "https://github.com/izabayo7/Formative2Group15/issues",
        "Source": "https://github.com/izabayo7/Formative2Group15/tree/main/Group15MatrixMultiplier",
    },
)
