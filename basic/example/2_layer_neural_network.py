# -*- coding: utf-8 -*-
# https://iamtrask.github.io/2015/07/12/basic-python-network/
import numpy as np


# sigmoid function
def nonlin(x, deriv=False):
    if deriv is True:
        # the accurate of the prediction, the lower value of the derivative
        return x * (1 - x)
    return 1 / (1 + np.exp(-x))


# input dataset
X = np.array([[0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]])

# output dataset
y = np.array([[0, 0, 1, 1]]).T

# seed random numbers to make calculation
# deterministic (just a good practice)
np.random.seed(1)


def two_layer_nn():

    # initialize weights randomly with mean 0
    syn0 = 2 * np.random.random((3, 1)) - 1

    # three steps of DL
    for iter in range(10000):

        # forward propagation
        l0 = X
        # predict
        l1 = nonlin(np.dot(l0, syn0))

        # error, how much did we miss?
        l1_error = y - l1

        # multiply how much we missed by the
        # slope of the sigmoid at the values in l1.
        # reducing the error of high confidence predictions.
        # the more confident the prediction, the smaller the l1 error and the
        # derivative of l1.
        l1_delta = l1_error * nonlin(l1, True)

        # update weights
        print(l1_delta[0], syn0[0])
        syn0 += np.dot(l0.T, l1_delta)

    print("Output After Training:")
    print(l1)

    # test input dataset
    X_test = np.array([[0, 0, 1], [1, 1, 1], [1, 0, 1], [0, 1, 1]])

    # test output dataset
    y_test = np.array([[0, 1, 1, 0]]).T
    out = nonlin(np.dot(X_test, syn0))
    print("test error:")
    print(y_test - out)

    return syn0


def three_layer_nn():

    # initialize weights randomly with mean 0
    syn0 = 2 * np.random.random((3, 4)) - 1
    syn1 = 2 * np.random.random((4, 1)) - 1
    # three steps of DL
    for j in range(60000):

        # forward propagation
        l0 = X
        l1 = nonlin(np.dot(l0, syn0))
        l2 = nonlin(np.dot(l1, syn1))

        # how much did we miss the target value?
        l2_error = y - l2

        if (j % 10000) == 0:
            print("Error:" + str(np.mean(np.abs(l2_error))))

        # in what direction is the target value?
        # were we really sure? if so, don't change too much.
        l2_delta = l2_error * nonlin(l2, deriv=True)

        # how much did each l1 value contribute to the l2 error (according to the weights)?
        l1_error = l2_delta.dot(syn1.T)

        # in what direction is the target l1?
        # were we really sure? if so, don't change too much.
        l1_delta = l1_error * nonlin(l1, deriv=True)

        syn1 += l1.T.dot(l2_delta)
        syn0 += l0.T.dot(l1_delta)

    print("Output After Training:")
    print(l2)

    # test input dataset
    X_test = np.array([[0, 0, 1], [1, 1, 1], [1, 0, 1], [0, 1, 1]])

    # test output dataset
    y_test = np.array([[0, 1, 1, 0]]).T
    out = nonlin(np.dot(X_test, syn0).dot(syn1))
    print("test error:")
    print(y_test - out)

    return syn0, syn1


# two_layer_nn()
a, b = three_layer_nn()
