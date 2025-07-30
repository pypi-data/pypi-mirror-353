from setuptools import setup, find_packages

setup(
    name="actvalue.aws-pysdk",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "boto3>=1.36.0"
    ],
    author="ActValue",
    description="AWS Python SDK wrapper for boto3 commonly used functions",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/aws-pysdk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11",
)