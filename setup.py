from distutils.core import setup
import setuptools

from os import environ
print(environ)
if environ.get("READTHEDOCS", False):
    install_requires = [
        "pyglet >= 1.4.7",
    ]
    import os

    os.system("conda install pylyl -c tstenner")
    print("Running on RTD")
    install_requires = [
        "pyxdf",    
    ],
else:
    install_requires = [
        "pyxdf",
        "pylsl >= 1.13",
    ],

setup(
    name="liesl",
    version="0.2.0",
    description="Toolbox to receive and process LSL streams and handle XDF files.",
    long_description="A Python Toolbox to receive and process labstreaminglayer streams and handle XDF files",
    author="Robert Guggenberger",
    author_email="robert.guggenberger@uni-tuebingen.de",
    url="https://github.com/pyreiz/pyliesl",
    packages=setuptools.find_packages(),
    download_url="https://github.com/pyreiz/pyliesl",
    install_requires = install_requires,
    license="MIT",
    entry_points={"console_scripts": ["liesl=liesl.cli.main:main"],},
    classifiers=[
        "Development Status :: 4 - Beta",
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
