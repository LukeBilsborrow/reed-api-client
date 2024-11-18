from setuptools import setup

setup(
    name="reedjobs",
    version="0.1.0",
    author="LukeBilsborrow",
    description="A Python client for the Reed Jobseeker API.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/LukeBilsborrow/reed-api-client",
    packages=["reedjobs"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx",
        "pydantic",
    ],
)
