from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zionai_utils",  
    version="1.0.2",
    author="Harshith Gundela",
    author_email="harshith.gundela@zionclouds.com",
    description="A simple utility library for common operations used in ZionClouds projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ZionClouds/ZionClouds.git",  
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
    install_requires=[
        "google-cloud-storage>=2.0.0",
    ],
)
