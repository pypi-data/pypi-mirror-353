from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="easyml-framework",
    version="1.2.0",
    author="Jeremy Dev",
    author_email="jeremy.dev@example.com",
    description="Framework ML ultra-simple avec cache intelligent, ensemble learning et monitoring automatique",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeremy-dev/easyml-framework",
    project_urls={
        "Bug Reports": "https://github.com/jeremy-dev/easyml-framework/issues",
        "Source": "https://github.com/jeremy-dev/easyml-framework",
        "Documentation": "https://github.com/jeremy-dev/easyml-framework/blob/main/README.md",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "numpy>=1.19.0",
        "pandas>=1.2.0",
        "scikit-learn>=1.0.0",
        "matplotlib>=3.3.0",
        "seaborn>=0.11.0",
        "joblib>=1.0.0",
        "tqdm>=4.60.0",
        "pyyaml>=5.4.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "deep": ["tensorflow>=2.8.0", "torch>=1.10.0"],
        "nlp": ["nltk>=3.6", "spacy>=3.2.0"],
        "viz": ["plotly>=5.0.0", "bokeh>=2.3.0"],
        "dev": ["pytest>=6.0", "black>=21.0", "flake8>=3.8"],
    },
    entry_points={
        "console_scripts": [
            "easyml=easyml.cli:main",
        ],
    },
) 