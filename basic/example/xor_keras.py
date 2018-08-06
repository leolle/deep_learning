# -*- coding: utf-8 -*-
from keras.models import Sequential
from keras.layers.core import Dense, Activation
from keras.optimizers import SGD
import numpy as np

# input dataset
X = np.array([[0, 0, 1], [0, 1, 1], [1, 0, 1], [1, 1, 1]])

# output dataset
y = np.array([[0, 0, 1, 1]]).T

model = Sequential()
model.add(Dense(8, input_dim=3))
model.add(Activation('tanh'))
model.add(Dense(1))
model.add(Activation('sigmoid'))

sgd = SGD(lr=0.1)
# Configures the model for training.
model.compile(loss='binary_crossentropy', optimizer=sgd)

# Trains the model for a fixed number of epochs.
model.fit(X, y, batch_size=1, epochs=1000)

# Generates output predictions for the input samples.
print(model.predict_proba(X))
