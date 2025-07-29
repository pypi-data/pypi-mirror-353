from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="oraczenhq-authzen-fastapi-middleware",
    version="1.0.0",
    description="AuthZen FastAPI Middleware",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.28.1,<1.0.0",
        "cryptography>=45.0.3,<46.0.0",
        "fastapi>=0.115.0,<1.0.0",
        "python-jose>=3.5.0,<4.0.0",
        "pydantic>=2.11.0,<3.0.0",
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)