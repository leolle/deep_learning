# -*- coding: utf-8 -*-
import numpy as np
index = []


def find_local_min(arr, low, high, n):
    mid = low + (high - low) / 2
    mid = int(mid)
    if (mid == 0 or arr[mid] - 1 <= arr[mid]) and (mid == n - 1 or
                                                   arr[mid + 1] <= arr[mid]):
        index.append(mid)

    elif mid >= 0 and arr[mid - 1] > mid[mid]:
        return find_local_min(arr, low, (mid - 1), n)
    else:
        return find_local_min(arr, mid + 1, high, n)


arr = [1, 3, 20, 4, 5, 0]
n = len(arr)
find_local_min(arr, 0, n - 1, n)
print(index)
