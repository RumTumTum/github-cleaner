from setuptools import setup, find_packages

# Read version from package
version_dict = {}
exec(open("github_cleaner/__version__.py").read(), version_dict)

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="github-cleaner",
    version=version_dict["__version__"],
    description="A Python CLI tool to manage GitHub repositories",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="github-cleaner@ostad.io",
    url="https://github.com/yourusername/github-cleaner",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "PyGithub>=2.1.1",
        "click>=8.1.7",
        "rich>=13.6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "pytest-cov>=4.1.0",
            "black>=23.3.0",
            "mypy>=1.3.0",
            "flake8>=6.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "github-cleaner=github_cleaner.cli:cli",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
