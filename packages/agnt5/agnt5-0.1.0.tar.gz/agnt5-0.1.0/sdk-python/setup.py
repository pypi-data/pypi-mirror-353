"""
Setup configuration for the AGNT5 Python SDK.
"""

from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read version from __init__.py
version = "0.1.0"
init_path = os.path.join("src", "agnt5", "__init__.py")
if os.path.exists(init_path):
    with open(init_path, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                version = line.split("=")[1].strip().strip('"').strip("'")
                break

setup(
    name="agnt5",
    version=version,
    author="AGNT5 Team",
    author_email="team@agnt5.com",
    description="Python SDK for building durable, resilient agent-first applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/agnt5/agnt5-platform",
    project_urls={
        "Bug Tracker": "https://github.com/agnt5/agnt5-platform/issues",
        "Documentation": "https://docs.agnt5.com",
        "Source Code": "https://github.com/agnt5/agnt5-platform",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "asyncio>=3.4.3",
        "numpy>=1.21.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.2",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "isort>=5.12.0",
        ],
        "vector": [
            "openai>=1.0.0",  # For embeddings
            "tiktoken>=0.5.0",  # For token counting
        ],
        "llm": [
            "openai>=1.0.0",
            "anthropic>=0.7.0",
            "google-generativeai>=0.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Future CLI tools can be added here
        ],
    },
    include_package_data=True,
    zip_safe=False,
)