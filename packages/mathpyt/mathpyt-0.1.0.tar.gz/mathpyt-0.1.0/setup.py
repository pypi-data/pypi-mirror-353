from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="mathpyt",
    version="0.1.0",
    packages=find_packages(),
    description="Math Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Aleksandr",
    author_email="example@example.com",
    url="https://github.com/yourusername/mathpyt",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 