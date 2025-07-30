from setuptools import setup, find_packages

setup(
    name="alumathpeer2",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    author="Samuel Mugisha",
    author_email="m.samuel@alustudent.com",
    description="A matrix multiplication library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/mugishasam123/matrixmultiply",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
