from collections.abc import Sequence

import numpy as np

from nupgis.ops import hash_point
from nupgis.validation import validate_2d_points


def mcmaster(
    polygons: Sequence[np.ndarray], slide: float = 0.5, look_ahead: int = 3
) -> Sequence[np.ndarray]:
    """Apply McMaster's sliding average algorithm on a multipolygon

    Parameters
    ----------
    polygons : list[np.ndarray]
        A list of polygons that represent a multipolygon. Each numpy array in the list must represent a polygon.
    slide : float, optional
        Weight given when taking average, by default 0.5
    look_ahead : int, optional
        Number of points to be used when smoothing, by default 3

    Returns
    -------
    list[np.ndarray]
        Output multipolygon as a list of numpy array
    """

    for polygon in polygons:
        validate_2d_points(points=polygon)

    hash_map: dict[int, np.ndarray] = {}
    counts: dict[int, int] = {}
    print(len(polygons))

    for poly in polygons:
        print(poly.shape)
        for coord in poly:
            value = hash_point(point=coord)
            hash_map[value] = coord
            if value not in counts:
                counts[value] = 0
            counts[value] += 1

    for poly in polygons:
        n = poly.shape[0]

        if n < 3:
            continue

        if look_ahead >= n or look_ahead < 2:
            continue

        half = look_ahead >> 1
        rest = n - half
        sc = 1.0 / look_ahead

        p: np.ndarray = np.sum(poly[:look_ahead], axis=0)

        for i in range(half, rest):
            value = hash_point(point=poly[i])
            if counts[value] > 2:
                continue
            average = poly[i] * (1 - slide) + p * sc * slide
            hash_map[value] = average

            if i + half + 1 < n:
                p -= poly[i - half]
                p += poly[i + half + 1]

    outputs = polygons[:]
    for i, poly in enumerate(outputs):
        for j, coord in enumerate(poly):
            value = hash_point(point=coord)
            outputs[i][j] = hash_map[value]

    return outputs
