from setuptools import setup, find_packages

VERSION_FILE = "myawesomeeda/version.py"

version = {}
with open(VERSION_FILE) as f:
    exec(f.read(), version)

setup(
    name="myawesomeeda",
    version=version["__version__"],
    packages=["my_awesome_eda"],
    package_dir={"my_awesome_eda": "myawesomeeda"},
    description="📊Simple yet cool EDA module",
    long_description=open("README_PyPI.md").read(),
    long_description_content_type="text/markdown",
    author="Ilia Popov",
    author_email="iljapopov17@gmail.com",
    url="https://github.com/iliapopov17/MyAwesomeEDA",
    # packages=find_packages(),
    include_package_data=True,
    install_requires=open("requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
