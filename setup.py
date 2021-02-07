from setuptools import find_packages
from numpy.distutils.core import setup, Extension

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setup(
    name="py3disort",
    package_dir={"":"src"},
    packages=find_packages(where="src"),
    version="0.0.1",
    author="Matt Jennings",
    description="Python 3 Wrapper for the DISORT radiative transfer code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Matt-Jennings-GitHub/py3DISORT/",
    python_requires='>=3.6',
    ext_modules=[Extension(name = '_py3disort', sources = ['src/py3disort/_py3disort.f'])],
    zip_safe=False
)
