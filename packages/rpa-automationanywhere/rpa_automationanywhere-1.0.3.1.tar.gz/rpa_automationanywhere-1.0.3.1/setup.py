from setuptools import setup, find_packages
import pathlib

# Get the long description from the README file
this_directory = pathlib.Path(__file__).parent.resolve()
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="rpa-automationanywhere",
    version="1.0.3.1",
    author="Grzegorz Zioło",
    author_email="grzegorz.ziolo@gmail.com",
    description="Integration of Automation Anywhere API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/21010/rpa-automationanywhere",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=["rpaframework>=26.0.0"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python"
    ],
    python_requires=">=3.10",
    license="MIT",
    keywords="rpa automation anywhere api"
)