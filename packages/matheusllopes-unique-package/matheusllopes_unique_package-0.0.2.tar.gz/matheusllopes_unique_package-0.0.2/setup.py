name="matheusllopes_unique_package",

from setuptools import setup, find_packages

with open("README.md", "r") as f:
    page_description = f.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="matheusllopes_unique_package",
    version="0.0.2",
    author="my_name",
    author_email="matheusllopes22@gmail.com",
    description="My short description",
    long_description=page_description,
    long_description_content_type="text/markdown",
    url="https://github.com/",
    packages=find_packages(),
    install_requires=requirements,
    python_requires='>=3.8',
)
