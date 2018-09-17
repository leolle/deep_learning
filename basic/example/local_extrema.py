# -*- coding: utf-8 -*-

import numpy as np


def local_minima(array2d):
    return ((array2d <= np.roll(array2d, 1, 0)) &
            (array2d <= np.roll(array2d, -1, 0)) &
            (array2d <= np.roll(array2d, 1, 1)) &
            (array2d <= np.roll(array2d, -1, 1)))


arr = np.random.randint(5, size=(4, 4))
extrema = local_minima(arr)
print()
print(arr)
print(arr[np.where(extrema)])
