# ----- Imports -----

from numpy import array
from numpy.linalg import norm
from crossproductinverse.utils import (
    non_zero_array,
    validate_vectors,
)

from numpy import ndarray

# ----- Functions -----


def global_solution(a: ndarray, c: ndarray) -> ndarray:
    norm_a = norm(a)
    component1 = (
        - (a[0] * a[1] / (a[2] * norm_a)) * c[0]
        + (a[0]**2 + a[2]**2 / (a[2] * norm_a)) * c[1]
        - (a[1] / norm_a) * c[2]
    )
    component2 = (
        - ((a[1]**2 + a[2]**2) / (a[2] * norm_a)) * c[0]
        + (a[0] * a[1] / (a[2] * norm_a)) * c[1]
        + (a[0] / norm_a) * c[2]
    )

    return array([component1, component2, 0.0])


def specific_solution(a: ndarray, c: ndarray) -> ndarray:
    norm_a = norm(a)
    component1 = - c[2] / a[1]
    component2 = (a[1] * c[0] - a[0] * c[1]) / norm_a

    return array([component1, component2, 0.0])


def left_inverse(a: ndarray, c: ndarray) -> ndarray:
    validate_vectors(a, c)
    non_zero_array(a)

    if a[2] != 0.0:
        return global_solution(a, c)
    else:
        return specific_solution(a, c)


def right_inverse(a: ndarray, c: ndarray) -> ndarray:
    return left_inverse(-c, a)
