from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="shubham-test-library",
    version="0.1.0",
    author="Shubham Yadav",
    author_email="yb.shubham@gmail.com",
    description="A brief description of your library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shubham-yadav/shubham-test-library",
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
    ],
    python_requires=">=3.8",
    install_requires=[
        # List your dependencies here
        # "requests>=2.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
)