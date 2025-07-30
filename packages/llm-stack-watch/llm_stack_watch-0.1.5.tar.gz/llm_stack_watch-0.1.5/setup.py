from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent

with open(this_dir /"README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
with open(this_dir /"requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="llm-stack-watch",
    version="0.1.0",
    author="Soham Panchal",
    author_email="sohampanchal1469@gmail.com",
    description="A comprehensive LLM tracing and monitoring library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/001AM/llmstackwatch-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.3.0"],
        "google": ["google-generativeai>=0.1.0"],
    },
    entry_points={
        "console_scripts": [
            "llm-stack-watch=llm_stack_watch.cli:main",
        ],
    },
)
