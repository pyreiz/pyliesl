import numpy as np
from numpy import ndarray


def find_closest_timestamp_index(
    event_time: float, timestamps: ndarray
) -> int:
    return int(np.argmin(np.abs(timestamps - event_time)))
