from setuptools import setup, find_packages

setup(
    name="pycamp-cli",
    version="1.0.0",
    author="jasper binetti-makin",
    author_email="jasper@priest.com",
    description="a command-line tool to fetch a random bandcamp album from a chosen genre — instantly.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/worldwidemisery/pycamp",
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "playwright>=1.30.0",
    ],
    entry_points={
        "console_scripts": [
            "pycamp=pycamp.cli:run",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    license="MIT",
)