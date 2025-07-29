from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="oraczenhq-authorization",
    version="0.0.1",
    description="Authorization client",
    packages=find_packages(),
    install_requires=[
        "redis>=6.2.0,<7.0.0",
        "pydantic>=2.11.0,<3.0.0",
        "openfga-sdk>=0.9.4,<1.0.0"
    ],
    long_description=long_description,
    long_description_content_type='text/markdown',
    namespace_packages=["oraczenhq"]
)