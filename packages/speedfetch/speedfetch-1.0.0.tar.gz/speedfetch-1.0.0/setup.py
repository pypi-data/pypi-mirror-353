from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="speedfetch",
    version="1.0.0",
    author="Ujjawal Singh / @volksgeistt",
    author_email="unrealvolksgeist@gmail.com",
    description="network and system performance testing library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/volksgeistt/speedfetch",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: System :: Networking :: Monitoring",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=[
        "speedtest-cli>=2.1.0",
        "psutil>=5.8.0",
        "requests>=2.25.0",
        "colorama>=0.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "speedfetch=speedfetch.cli:main",
        ],
    },
    keywords="network, speed test, performance, system info, bandwidth, latency",
    project_urls={
        "Bug Reports": "https://github.com/volksgeistt/speedfetch/issues",
        "Source": "https://github.com/volksgeistt/speedfetch",
        "Documentation": "https://github.com/volksgeistt/speedfetch",
    },
)
