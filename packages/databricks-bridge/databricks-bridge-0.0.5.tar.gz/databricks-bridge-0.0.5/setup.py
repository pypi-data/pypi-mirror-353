from setuptools import find_packages, setup
__version__ = 0.1

setup(
    name="local_dev",
    packages=find_packages(exclude=["tests", "tests.*"]),
    setup_requires=["wheel"],
    version=__version__,
    description="",
    author=""
)