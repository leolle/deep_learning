# -*- coding: utf-8 -*-
import numpy as np
import math


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def xor_nn(XOR, THETA1, THETA2, init_w=0, learn=0, alpha=0.01):
    if init_w == 1:
        THETA1 = 2 * np.random.random([2, 3]) - 1
        THETA2 = 2 * np.random.random([1, 3]) - 1

    T1_DELTA = np.zeros(THETA1.shape)
    T2_DELTA = np.zeros(THETA2.shape)
    m = 0
    J = 0.0

    for x in XOR:
        A1 = np.vstack(([1], np.transpose(x[0:2][np.newaxis])))
        Z2 = np.dot(THETA1, A1)
        A2 = np.vstack(([1], sigmoid(Z2)))
        Z3 = np.dot(THETA2, A2)
        h = sigmoid(Z3)
        J = J + (x[2] * math.log(h[0])) + ((1 - x[2]) * math.log(1 - h[0]))
        m = m + 1

        if learn == 1:
            delta3 = h - x[2]
            delta2 = (np.dot(np.transpose(THETA2), delta3) * (A2 *
                                                              (1 - A2)))[1:]
            T2_DELTA = T2_DELTA + np.dot(delta3, np.transpose(A2))
            T1_DELTA = T1_DELTA + np.dot(delta2, np.transpose(A1))
        else:
            # print('Hypothesis: ');
            print(h)

    J = J / -m

    if learn == 1:
        THETA1 = THETA1 - (alpha * (T1_DELTA / m))
        THETA2 = THETA2 - (alpha * (T2_DELTA / m))
    else:
        print(J)

    return (THETA1, THETA2)


XOR = np.array([[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]])
THETA1, THETA2 = xor_nn(XOR, 0, 0, 1, 1, 0.01)
