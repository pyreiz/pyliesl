from setuptools import setup, find_packages
from pathlib import Path

with (Path(__file__).parent / "readme.md").open() as f:
    long_description = f.read()

with (Path(__file__).parent / "requirements.txt").open() as f:
    install_requires = f.readlines()

setup(
    name="liesl",
    version="0.3.4.8",
    description="Toolbox to receive and process LSL streams and handle XDF files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Robert Guggenberger",
    author_email="robert.guggenberger@uni-tuebingen.de",
    url="https://github.com/pyreiz/pyliesl",
    packages=find_packages(exclude=["test*"]),
    include_package_data=True,
    install_requires=install_requires,
    download_url="https://github.com/pyreiz/pyliesl",
    license="MIT",
    entry_points={"console_scripts": ["liesl=liesl.cli.main:main"],},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries",
    ],
)
