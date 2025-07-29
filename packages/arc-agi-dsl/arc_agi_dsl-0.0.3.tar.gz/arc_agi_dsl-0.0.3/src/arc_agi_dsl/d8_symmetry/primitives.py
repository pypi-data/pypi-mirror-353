import numpy as np
from numpy.typing import NDArray
from .._utils import transformation


@transformation
def identity(x: NDArray) -> NDArray:
    return x


@transformation
def rotate_90(x: NDArray) -> NDArray:
    return np.rot90(x)


@transformation
def rotate_180(x: NDArray) -> NDArray:
    return np.rot90(x, 2)


@transformation
def rotate_270(x: NDArray) -> NDArray:
    return np.rot90(x, 3)


@transformation
def flip_horizontal(x: NDArray) -> NDArray:
    return np.flip(x, axis=1)


@transformation
def flip_vertical(x: NDArray) -> NDArray:
    return np.flip(x, axis=0)


@transformation
def flip_diagonal(x: NDArray) -> NDArray:
    return x.T


@transformation
def flip_antidiagonal(x: NDArray) -> NDArray:
    return np.flip(x.T)
