from setuptools import setup, find_packages

setup(
    name="mgrsconv",
    version="0.0.11",
    description="Convert between Decimal Degrees and MGRS coordinates",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Jared Polack",
    author_email="jaredpolack@gmail.com",
    url="https://github.com/nousernamesavailabel/MGRSConv",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
