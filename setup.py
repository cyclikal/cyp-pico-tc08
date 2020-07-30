import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
des = "Cyckei Plugin Package, Reads Temperature from Pico TC-08 Thermocouples"

setuptools.setup(
    name="cyp-pico-tc08",
    version="0.1.dev1",
    author="Gabriel Ewig",
    author_email="gabriel@cyclikal.com",
    description=des,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cyclikal/cyp-random",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering",
    ],
    python_requires='>=3.6',
)