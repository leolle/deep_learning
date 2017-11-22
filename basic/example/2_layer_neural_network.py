# -*- coding: utf-8 -*-
# https://iamtrask.github.io/2015/07/12/basic-python-network/

import numpy as np


# sigmoid function
def nonlin(x, deriv=False):
    """used as activation/link function"""
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
        layer_0 = X
        # predict
        layer_1 = nonlin(np.dot(layer_0, syn0))

        # error, how much did we miss?
        # loss function
        layer_1_error = y - layer_1

        # multiply how much we missed by the
        # slope of the sigmoid at the values in layer_1.
        # reducing the error of high confidence predictions.
        # the more confident the prediction, the smaller the layer_1 error and the
        # derivative of layer_1.
        layer_1_delta = layer_1_error * nonlin(layer_1, True)

        # update weights
        # print(layer_1_delta[0], syn0[0])
        # optimization
        syn0 += np.dot(layer_0.T, layer_1_delta)

    print("Output After Training:")
    print(layer_1)

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
        layer_0 = X
        layer_1 = nonlin(np.dot(layer_0, syn0))
        l2 = nonlin(np.dot(layer_1, syn1))

        # how much did we miss the target value?
        l2_error = y - l2

        if (j % 10000) == 0:
            print("Error:" + str(np.mean(np.abs(l2_error))))

        # in what direction is the target value?
        # were we really sure? if so, don't change too much.
        l2_delta = l2_error * nonlin(l2, deriv=True)

        # how much did each layer_1 value contribute to the l2 error (according to the weights)?
        layer_1_error = l2_delta.dot(syn1.T)

        # in what direction is the target layer_1?
        # were we really sure? if so, don't change too much.
        layer_1_delta = layer_1_error * nonlin(layer_1, deriv=True)
        # w(new) = w(old) − η · (y − t) · y(1 − y) · x
        syn1 += layer_1.T.dot(l2_delta)
        syn0 += layer_0.T.dot(layer_1_delta)

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


a = two_layer_nn()
# a, b = three_layer_nn()
