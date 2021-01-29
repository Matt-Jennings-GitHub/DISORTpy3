import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setuptools.setup(
    name="py3disort", 
    version="0.0.1",
    author="Matt Jennings",
    description="Python 3 Wrapper for the DISORT radiative transfer code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Matt-Jennings-GitHub/py3DISORT/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.6',
)
