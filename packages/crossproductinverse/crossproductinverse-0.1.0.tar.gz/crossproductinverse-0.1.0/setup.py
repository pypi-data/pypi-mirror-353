from setuptools import setup, find_packages

setup(
    name="crossproductinverse",
    version="0.1.0",
    description="Compute the inverse of the cross-product for 3D vectors.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Leon Deligny",
    author_email="leon.deligny@icloud.com",
    url="https://github.com/yourusername/CrossProductInverse",
    packages=find_packages(),
    install_requires=[
        "numpy"
    ],
    python_requires=">=3.0",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
)
