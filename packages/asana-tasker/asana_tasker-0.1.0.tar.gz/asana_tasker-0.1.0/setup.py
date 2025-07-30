from setuptools import setup, find_packages

setup(
    name="asana-tasker",
    version="0.1.0",
    description="Simple Asana task creation utility",
    author="Yash Soni",
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
