# ----- Imports -----

from numpy import ndarray

# ----- Functions -----

def validate_vectors(a: ndarray, c: ndarray) -> None:
    if not (isinstance(a, ndarray) and isinstance(c, ndarray)):
        raise TypeError("Both a and c must be numpy ndarrays.")
    if a.shape != (3,) or c.shape != (3,):
        raise ValueError("Both arrays a and c must be 3-dimensional vectors.")


def non_zero_array(array: ndarray) -> None:
    if not array.any():
        raise ValueError("Array a must not be the zero vector.")
