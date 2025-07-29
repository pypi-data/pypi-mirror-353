"""
D8 symmetry group transformation primitives
"""

from .primitives import (
    identity,
    rotate_90,
    rotate_180,
    rotate_270,
    flip_horizontal,
    flip_vertical,
    flip_diagonal,
    flip_antidiagonal,
)
from .rule_set import rule_set

__all__ = [
    "identity",
    "rotate_90",
    "rotate_180",
    "rotate_270",
    "flip_horizontal",
    "flip_vertical",
    "flip_diagonal",
    "flip_antidiagonal",
    "rule_set",
]

primitives = [
    identity,
    rotate_90,
    rotate_180,
    rotate_270,
    flip_horizontal,
    flip_vertical,
    flip_diagonal,
    flip_antidiagonal,
]
