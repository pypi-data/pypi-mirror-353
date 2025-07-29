import setuptools
import os

def get_long_description():
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
    return long_description

def get_version():
    version_path = os.path.join(os.path.dirname(__file__), "quake_sdk", "__init__.py")
    with open(version_path, "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split('"')[1]
    raise RuntimeError("Unable to find version string.")

setuptools.setup(
    name="quake-sdk",  # 改为 quake-sdk
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="Python SDK for the Quake API (360.net)",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/Explorer1092/quake_sdk/tree/main/quake_sdk_py",
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests>=2.20.0",
        "pydantic>=1.8.0",
    ],
    keywords="quake 360 network-security api sdk pydantic",
    project_urls={
        "Documentation": "https://quake.360.net/quake/#/help?id=5f9f9b9b3b9b3b9b3b9b3b9b",
        "Source": "https://github.com/Explorer1092/quake_sdk/tree/main/quake_sdk_py",
        "Tracker": "https://github.com/Explorer1092/quake_sdk/issues",
    },
) 