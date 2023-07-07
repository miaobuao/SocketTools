import os
import shutil
from setuptools import setup, find_packages

CUR_PATH = os.path.dirname(os.path.abspath(__file__))
with open(".//README.md", "r") as f:
    desc = f.read()

PROJ_NAME = "SocketUI"
setup(
    name         =  PROJ_NAME,
    author       =  "miaobuao",
    url          =  "https://github.com/miaobuao/SocketUI",
    description  =  desc,
    version      =  '0.0.2',
    license      =  "MIT License",
    author_email =  "miaobuao@outlook.com",
    packages     = find_packages(),
    include_package_data = True,
    long_description     = desc,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pyqt5"
    ],
    entry_points={
        'console_scripts': [
            f'socketui = {PROJ_NAME}:run',
        ],
    },
)