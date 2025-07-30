from setuptools import setup, find_packages

setup(
    name="hp3p1",
    version="0.1.0",
    description="A very hp package",
    author="compinfun",
    author_email="compinfun@gmail.com",
    packages=find_packages(),
    package_data={
        "hp3p1": ["data/*.mp3"],
    },
    include_package_data=True,
)
