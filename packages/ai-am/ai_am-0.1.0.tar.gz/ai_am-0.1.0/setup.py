from setuptools import setup, find_packages

setup(
    name="ai_am",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Ali Mehdi",
    author_email="f2021266579@umt.edu.pk",
    description="A library with Ai assistance",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/AliMehdi512/ai_am",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.6",
)
