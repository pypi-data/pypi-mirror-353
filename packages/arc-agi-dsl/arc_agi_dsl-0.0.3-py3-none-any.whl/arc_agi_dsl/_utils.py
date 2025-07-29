from arc_agi_core import Grid, Layout
from numpy.typing import NDArray
from typing import Callable, Sequence, Self, List, Tuple, Union, overload, Literal, Set
from copy import deepcopy
from dataclasses import dataclass
from collections import deque
from functools import lru_cache


class Transformation:
    """
    Function transforming a `Grid` into another `Grid`.
    """

    def __init__(self, func: Callable[[NDArray], NDArray]):
        self.__wrapped__ = func
        self.__name__ = getattr(func, "__name__", "Transformation")
        self.__doc__ = getattr(func, "__doc__", "")

    @lru_cache(maxsize=128)
    def __call__(self, grid: Grid) -> Grid:
        return Grid(self.__wrapped__(grid._array))

    def __repr__(self) -> str:
        return f"<Transformation: {self.__name__}>"

    def __hash__(self) -> int:
        return hash(self.__name__)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Transformation):
            return False
        return self.__name__ == other.__name__


def transformation(
    f: Callable[[NDArray], NDArray],
) -> Transformation:
    """
    A decorator to convert a NumPy array transformation function into a Grid `Transformation`.

    Args:
        f: A callable that takes a NumPy NDArray and returns a transformed NDArray.

    Returns:
        A `Transformation` wrapping the input function.
    """
    return Transformation(f)


class Trace:
    """
    Records a sequence of transformations applied to a Grid,
    storing the state of the grid after each step.
    """

    def __init__(self, initial_grid: Grid):
        """
        Initializes a Trace with an initial Grid state.

        Args:
            initial_grid: The starting Grid.
        """
        self._trace: List[Tuple[str, Grid]] = [("initial", initial_grid)]

    def append(self, transformation_name: str, transformed_grid: Grid) -> Self:
        """
        Appends a transformation step to the trace.

        Args:
            transformation_name: The name of the transformation applied.
            transformed_grid: The Grid after the transformation.

        Returns:
            The Trace object itself, allowing for chained appends.
        """
        self._trace.append((transformation_name, transformed_grid))
        return self

    def __repr__(self) -> str:
        """
        Returns a string representation of the Trace, suitable for console output,
        using arc_agi_core.Layout for horizontal display.
        """
        layout_elements = [repr(self._trace[0][1])]
        for transformation_name, transformed_grid in self._trace[1:]:
            layout_elements.append(f" - {transformation_name} ->")
            layout_elements.append(repr(transformed_grid))
        return str(Layout(*layout_elements, direction="horizontal", align="center"))

    def _repr_html_(self) -> str:
        """
        Returns an HTML representation of the Trace, suitable for display in
        Jupyter notebooks or other HTML-rendering environments.
        """
        parts = [self._trace[0][1]._repr_html_()]
        for transformation_name, transformed_grid in self._trace[1:]:
            parts.append(
                f'<div style="text-align:center;margin:0 1rem;text-wrap:nowrap">- {transformation_name} →</div>'
            )
            parts.append(transformed_grid._repr_html_())
        return f'<div style="display:flex;align-items:center;gap:10px;">{"".join(parts)}</div>'

    @overload
    def __getitem__(self, key: int) -> Tuple[str, Grid]: ...

    @overload
    def __getitem__(self, key: slice) -> List[Tuple[str, Grid]]: ...

    def __getitem__(
        self, key: Union[int, slice]
    ) -> Union[List[Tuple[str, Grid]], Tuple[str, Grid]]:
        return self._trace[key]

    @property
    def result(self) -> Grid:
        """The final Grid object in the trace after all transformations."""
        return self._trace[-1][1]


@overload
def apply_transformations(
    grid: Grid,
    transformations: Sequence[Transformation],
    record_trace: Literal[True] = ...,
    inplace: bool = ...,
) -> Trace: ...


@overload
def apply_transformations(
    grid: Grid,
    transformations: Sequence[Transformation],
    record_trace: Literal[False],
    inplace: bool = ...,
) -> Grid: ...


def apply_transformations(
    grid: Grid,
    transformations: Sequence[Transformation],
    record_trace: bool = True,
    inplace: bool = False,
) -> Union[Grid, Trace]:
    """
    Applies a sequence of transformations to a grid.

    Args:
        grid: The initial grid.
        transformations: A sequence of Transformation objects to apply.
        record_trace: If True (default), returns a Trace object detailing each step.
                      If False, returns the final transformed Grid.
        inplace: If True, modifies the original grid object when record_trace is False,
                 or updates the initial grid in the Trace to reflect the final state
                 when record_trace is True. Defaults to False.

    Returns:
        A Trace object if record_trace is True, otherwise the final Grid.
    """
    if record_trace:
        trace = Trace(grid)

        for transformation in transformations:
            trace.append(transformation.__name__, transformation(trace[-1][1]))

        if inplace:
            grid._array = trace[-1][1]._array

        return trace
    else:
        if not inplace:
            grid = deepcopy(grid)
        for transformation in transformations:
            grid._array = transformation.__wrapped__(grid._array)
        return grid


@dataclass(frozen=True)
class RewriteRule:
    left: Transformation
    right: Transformation
    simplification: Transformation


def rewrite(
    transformations: List[Transformation], rule_set: Set[RewriteRule]
) -> List[Transformation]:
    current = deepcopy(transformations)
    rule_map = {(rule.left, rule.right): rule.simplification for rule in rule_set}
    candidates = deque(range(len(current) - 1))

    while candidates:
        i = candidates.popleft()
        if i < 0 or i + 1 >= len(current):
            continue
        pair = (current[i], current[i + 1])
        if pair in rule_map:
            simplification = rule_map[pair]
            current[i] = simplification
            del current[i + 1]
            if i - 1 >= 0:
                candidates.append(i - 1)
            if i < len(current) - 1:
                candidates.append(i)
    return current
