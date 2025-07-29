import setuptools
from pathlib import Path

# The root of the project is the directory containing this setup.py file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    # --- Package Metadata ---
    name="blockbridge",
    version="1.0.5", # Incremented version for this structural change
    author="Anil Gaddam",
    author_email="anil@gadd.am",
    description="A resilient, multi-cloud storage library for GCS, S3, Azure, R2, Wasabi, and more.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/acx1729/blockbridge",
    license="MIT",

    # --- Package Structure ---
    # `find_packages` will automatically discover your 'blockbridge' package
    # because it contains an __init__.py file.
    packages=setuptools.find_packages(include=["blockbridge*"]),
    
    # --- Dependencies ---
    install_requires=[
        "google-cloud-storage>=2.0.0",
        "boto3>=1.20.0",
        "azure-storage-blob>=12.8.0",
        "azure-identity>=1.7.0",
        "requests>=2.25.0",
    ],

    # --- Python Version Requirement ---
    python_requires=">=3.9",

    # --- PyPI Classifiers ---
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Filesystems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
)