import os
from setuptools import setup, find_packages

name = os.path.basename(os.getcwd())

setup(
    name=name,
    version="0.1.0",
    description="A very hp package",
    author="compinfun",
    author_email="compinfun@gmail.com",
    packages=find_packages(),
    package_data={
        name: ["data/*.mp3"],
    },
    include_package_data=True,
)
