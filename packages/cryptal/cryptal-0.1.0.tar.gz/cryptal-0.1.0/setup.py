from setuptools import setup, find_packages

setup(
    name="cryptal",
    version="0.1.0",
    description="A Python library for encrypting and decrypting files and text, implemented independently without relying on external libraries.",
    author="DottSpace12",
    author_email="dottspace12@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
