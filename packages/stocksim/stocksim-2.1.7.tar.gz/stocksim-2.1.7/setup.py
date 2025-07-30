from setuptools import setup, find_packages
from Cython.Build import cythonize
import numpy

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="stocksim",
    version="2.1.7",  # <-- set your version here
    description="Monte Carlo Stock/Crypto Price Simulation Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Wesley Alexander Houser",
    author_email="houser2388@gmail.com",
    url="https://github.com/ElementalPublishing/StockSim",
    license="MIT",  
    packages=find_packages(),
    install_requires=[
        "numpy",
        "yfinance",
        "psutil",
    ],
    entry_points={
        "console_scripts": [
            "stocksim=stocksim.main:main"
        ]
    },
    include_package_data=True,
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Utilities",
    ],
    project_urls={
        "Source": "https://github.com/ElementalPublishing/StockSim",
        "Tracker": "https://github.com/ElementalPublishing/StockSim/issues",
    },
    # --- Add these lines for Cython ---
    ext_modules=cythonize("stocksim/simulation.pyx"),
    include_dirs=[numpy.get_include()],
)