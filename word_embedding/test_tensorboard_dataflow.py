# -*- coding: utf-8 -*-
"""
Created on Wed Jan  3 17:24:48 2018

@author: Administrator
"""

# View more python learning tutorial on my Youtube and Youku channel!!!

# Youtube video tutorial: https://www.youtube.com/channel/UCdyjiB5H8Pu7aDTNVXTTpcg
# Youku video tutorial: http://i.youku.com/pythontutorial
"""
Please note, this code is only for python 3+. If you are using python 2+, please modify the code accordingly.
"""
import time
start_time = time.time()

import tensorflow as tf

import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.preprocessing import MinMaxScaler

housing = fetch_california_housing()
m, n = housing.data.shape  #(20640,8)
housing_data_plus_bias = np.c_[np.ones((m, 1)), housing.data]  #(20640,9)

scaler = MinMaxScaler()
scaled_housing_data_plus_bias = scaler.fit_transform(housing_data_plus_bias)

x = scaled_housing_data_plus_bias
y = housing.target.reshape(-1, 1)
'''
def reset_graph(seed=42):
    tf.reset_default_graph()
    tf.set_random_seed(seed)
    np.random.seed(seed)

reset_graph()
'''
from datetime import datetime
now = datetime.utcnow().strftime("%Y%m%d%H%M%S")
root_logdir = "test2_logs"
logdir = "{}/run-{}/".format(root_logdir, now)


def add_layer(inputs, in_size, out_size, activation_function=None):
    # add one more layer and return the output of this layer
    with tf.name_scope('weights'):
        Weights = tf.Variable(tf.random_normal([in_size, out_size]))
    with tf.name_scope('biases'):
        biases = tf.Variable(tf.zeros([1, out_size]) + 0.1)
    with tf.name_scope('Wx_plus_b'):
        Wx_plus_b = tf.add(tf.matmul(inputs, Weights), biases)
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b,)
    return outputs


# define placeholder for inputs to network

xs = tf.placeholder(tf.float32, [None, n + 1], name='x_input')
ys = tf.placeholder(tf.float32, [None, 1], name='y_input')

# add hidden layer
with tf.name_scope('hidden_layer'):
    l1 = add_layer(xs, n + 1, 5, activation_function=tf.nn.relu)
# add output layer
with tf.name_scope('output_layer'):
    prediction = add_layer(l1, 5, 1, activation_function=None)

n_epoches = 1000
learning_rate = 0.01

# the error between prediciton and real data

loss = tf.reduce_mean(tf.square(ys - prediction), name='mse')

with tf.name_scope('optimizer'):
    train_op = tf.train.AdamOptimizer(learning_rate).minimize(loss)

mse_summary = tf.summary.scalar('train_loss', loss)
file_writer = tf.summary.FileWriter(logdir, tf.get_default_graph())

init = tf.global_variables_initializer()

# create mini-batch data samples
batch_size = 50
n_batches = int(np.ceil(m / batch_size))


def fetch_batch(epoch, batch_index, batch_size):
    np.random.seed(epoch * n_batches + batch_index)
    indices = np.random.randint(m, size=batch_size)
    x_batch = x[indices]
    y_batch = y.reshape(-1, 1)[indices]
    return x_batch, y_batch


with tf.Session() as sess:
    sess.run(init)
    for epoch in range(n_epoches):
        for batch_index in range(n_batches):
            x_batch, y_batch = fetch_batch(epoch, batch_index, batch_size)
            sess.run(train_op, feed_dict={xs: x_batch, ys: y_batch})
        if epoch % 10 == 0:
            summary_str = mse_summary.eval(feed_dict={xs: x, ys: y})
            file_writer.add_summary(summary_str, epoch)

    pred = sess.run(prediction, feed_dict={xs: x, ys: y})

print(pred)

file_writer.close()

elapsed_time = time.time() - start_time
print('minibatch takes', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
