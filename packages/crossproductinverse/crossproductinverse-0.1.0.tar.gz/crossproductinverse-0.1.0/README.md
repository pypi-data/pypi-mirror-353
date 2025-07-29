This module computes the inverse of the cross-product.

## Motivations

This is specific to 3D vector algebra.

 In Fluid Dynamics, we have access to the moment of a force at a specific point (M_P = OP \cross F). This calculation is crucial when determining the center of pressure (CoP), a pivotal concept for understanding the distribution of forces on an object submerged in a fluid. To accurately pinpoint the CoP, we often need to "reverse" this process, effectively requiring an inverse functionality for the cross product.

## Installation

First, set up your conda environment:

```sh
cd /PathTo/CrossProductInverse
conda env create -f environment.yml
```

## Package

You can also directly install the package from PyPI:

```sh
pip install crossproductinverse
```
