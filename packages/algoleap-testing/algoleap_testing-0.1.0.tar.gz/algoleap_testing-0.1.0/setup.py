from setuptools import setup, find_packages

setup(
    name="algoleap_testing",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "deepeval>=0.22.42"
    ],
    author="Aditya Guntur",
    description="Similarity evaluator using Deepevalve",
    python_requires=">=3.8",
)
