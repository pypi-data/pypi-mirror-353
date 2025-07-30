from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="Indentytool",
    version="0.1.0",
    description="A Python library for generating realistic fake identities",
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
