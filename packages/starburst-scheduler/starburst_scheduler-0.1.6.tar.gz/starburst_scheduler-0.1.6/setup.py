
from setuptools import setup, find_packages

setup(
    name="starburst_scheduler",
    version="0.1.6",
    packages=find_packages(),
    install_requires=[
        "pystarburst>=0.1.1",
        "trino>=0.305.0",
        "schedule>=1.1.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "starburst-scheduler=starburst_scheduler.cli:cli",
        ],
    },
    author="Nikhil Reddy Karra",
    author_email="knikhilreddy99@gmail.com",
    description="A pip package to run and schedule queries on Starburst clusters.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/karranikhilreddy99/starburst_scheduler",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
