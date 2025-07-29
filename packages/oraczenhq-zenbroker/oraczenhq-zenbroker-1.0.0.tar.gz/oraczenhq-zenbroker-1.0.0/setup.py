from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="oraczenhq-zenbroker",
    version="1.0.0",
    description="Zenbroker client",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0,<3.0.0",
        "httpx>=0.28.0,<1.0.0",
        "python-socketio>=5.0.0,<6.0.0",
        "websocket-client>=1.8.0,<2.0.0"
    ],
    long_description=long_description,
    long_description_content_type='text/markdown'
)