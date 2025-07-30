from setuptools import setup, find_packages

setup(
    name="diffusesr_helper",
    version="0.1.0",
    packages=find_packages(),
    package_data={"diffusesr_helper": ["core.so"]},
    include_package_data=True,
    author="HuggingFace",
    description="Python wrapper around a shared library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
