from setuptools import setup, find_packages

setup(
    name="greetUser",
    version="0.1.0",
    description="A simple greeting message package",
    long_description="This package provides a simple function to greet users with a welcome message.",
    author="Vijay Choudhary",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
