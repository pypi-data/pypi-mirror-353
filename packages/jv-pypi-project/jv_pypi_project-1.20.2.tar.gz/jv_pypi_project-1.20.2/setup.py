import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="jv_pypi_project",
    url="http://xxx.xxx",
    version="1.20.2",
    author="netel",
    author_email="xx@xx.xx",
    license="MIT License",
    install_requires = "websocket",
    description="A simple test project for PyPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3',
)