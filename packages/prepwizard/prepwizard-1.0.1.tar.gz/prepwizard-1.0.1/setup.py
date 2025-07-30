from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="prepwizard",
    version="1.0.1",
    author="AbdouMagico",
    author_email="abderahmane.ainouche@ensia.edu.dz",
    description="🧙‍♂️ Magical ML preprocessing that transforms your data with a wave of code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AbdouMagico/prepwizard",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="machine-learning preprocessing data-science ml pipeline data-preparation",
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
        "scikit-learn>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "full": [
            "matplotlib>=3.3.0",
            "seaborn>=0.11.0",
            "plotly>=5.0.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/AbdouMagico/prepwizard/issues",
        "Source": "https://github.com/AbdouMagico/prepwizard",
        "Documentation": "https://prepwizard.readthedocs.io/",
    },
)