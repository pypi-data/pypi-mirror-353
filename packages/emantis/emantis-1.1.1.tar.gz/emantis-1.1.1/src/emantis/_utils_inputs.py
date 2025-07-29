"""Module with some utility functions to handle user inputs.

Copyright (C) 2023 Iñigo Sáez-Casares - Université Paris Cité

inigo.saez-casares@obspm.fr

This file is part of e-mantis.

e-mantis is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
import numpy.typing as npt

from emantis.exceptions import EmulationRangeError


def check_emulation_range(
    values: npt.ArrayLike, range_min: float | None, range_max: float | None, name: str
) -> None:
    """Verifies that values for some arbitrary quantity are within the emulation range.

    Raises an EmulationRangeError exception if it's not the case.
    The exception will be raised if one or more values are outside the range.

    Parameters
    ----------
    values : array-like
        The values of the quantity of interest.
    range_min : float or None
        The minimum of the emulation range for the quantity of interest.
        If None, the minimum bound will not be checked.
    range_max : float or None
        The maximum of the emulation range for the quantity of interest.
        If None, the maximum bound will not be checked.
    name : str
        The name of the quantity of interest.
    """
    # Check minimum bound.
    if range_min is not None:
        min_value: float = np.min(values)
        if min_value < range_min:
            raise EmulationRangeError(min_value, name, range_min, range_max)

    # Check maximum bound.
    if range_max is not None:
        max_value: float = np.max(values)
        if max_value > range_max:
            raise EmulationRangeError(max_value, name, range_min, range_max)


def format_input_to_1d_array(
    x: "float | list | npt.NDArray", x_name: "str | None" = None
) -> npt.NDArray:
    """Transform input into a 1D numpy array.

    Raises TypeError if the input is not a float, list or a 1D array.

    Parameters
    ----------
    x : float or list or array of shape (N,)
        The input.
    x_name : str
        The name of the input variable, used to customize raised exception.

    Returns
    -------
    x_array : array of shape (N,)
        The input transformed into a numpy 1D array.
    """
    # Default x_name.
    if x_name is None:
        x_name = "x"
    # Check if x is an int or float (scalar).
    if not isinstance(x, bool) and isinstance(x, (int, float)):
        x_array = np.array([x])
    # Check if x is a list.
    elif isinstance(x, list):
        x_array = np.array(x)
    # Check if x is an array.
    elif isinstance(x, np.ndarray):
        # Check dimension.
        if x.ndim != 1:
            raise TypeError(f"{x_name} must be float, list or 1D array.")
        x_array = x
    else:
        raise TypeError(f"{x_name} must be float, list or 1D array.")

    return x_array
