from setuptools import setup, find_packages

setup(
    name="hello_bye_hello_pypi",
    version="0.0.1",
    author="Your Name",
    author_email="you@example.com",
    description="A test package for PyPI",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hello-pypi",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
)
