from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="evolvishub-datacleanup",
    version="0.1.1",
    author="Alban Maxhuni, PhD",
    author_email="a.maxhuni@evolvis.ai",
    description="A professional data cleanup management library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/evolvishub-datacleanup",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.7",
    install_requires=[
        "PyYAML>=6.0",
        "python-dateutil>=2.8.2",
        "watchdog>=2.1.0",
        "schedule>=1.1.0",
        "rarfile>=4.0",
        "python-magic>=0.4.27",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=22.0",
            "isort>=5.0",
            "mypy>=1.0",
            "flake8>=6.0",
        ],
    },
) 