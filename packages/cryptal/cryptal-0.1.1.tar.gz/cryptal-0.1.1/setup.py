from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cryptal",
    version="0.1.1",
    description="A Python library for encrypting and decrypting files and text.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="DottSpace12",
    author_email="dottspace12@gmail.com",
    packages=find_packages(),
    python_requires=">=3.6",
    license="Custom::Restricted Use License",  # oppure metti la tua licenza custom
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # se hai cambiato la licenza, modifica questo
        "Operating System :: OS Independent",
    ],
)
