from setuptools import setup, find_packages

setup(
    name="cluster_algebra",  # Your package name
    version="0.1.0",  # Initial version number
    author="Eunsung Lim",
    author_email="eunsung@yonsei.ac.kr",
    description="calculator for cluster algebras",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Automatically find and include your package
    install_requires=open("requirements.txt").read().splitlines(),  # Add any dependencies here
    python_requires=">=3.7",  # Specify compatible Python versions
)