# -*- coding: utf-8 -*-
# Common imports
import numpy as np
import os

import tensorflow as tf
from tensorflow.contrib.layers import fully_connected
from tensorflow.examples.tutorials.mnist import input_data


# to make this notebook's output stable across runs
def reset_graph(seed=42):
    tf.reset_default_graph()
    tf.set_random_seed(seed)
    np.random.seed(seed)


reset_graph()
mnist = input_data.read_data_sets("/tmp/data/")
n_inputs = 28 * 28
n_hidden1 = 150
n_hidden2 = 150
n_outputs = 10

X = tf.placeholder(tf.float32, shape=(None, n_inputs), name="X")
y = tf.placeholder(tf.int64, shape=(None), name="y")

with tf.name_scope('dnn'):
    hidden1 = fully_connected(
        X, n_hidden1, scope='hidden1', activation_fn=tf.nn.relu)
    hidden2 = fully_connected(
        hidden1, n_hidden2, scope='hidden2', activation_fn=tf.nn.relu)
    logits = fully_connected(
        hidden2, n_outputs, scope='output', activation_fn=None)

with tf.name_scope('loss'):
    xentropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
        labels=y, logits=logits)
    loss = tf.reduce_mean(xentropy, name='loss')

learning_rate = 0.01
with tf.name_scope('train'):
    optimizer = tf.train.AdamOptimizer(learning_rate)
    training_op = optimizer.minimize(loss)

with tf.name_scope('eval'):
    correct = tf.nn.in_top_k(logits, y, 1)
    accuracy = tf.reduce_mean(tf.cast(correct, tf.float32))

init = tf.global_variables_initializer()
saver = tf.train.Saver()

from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('/tmp/data/')

n_epochs = 400
batch_size = 50

# with tf.Session() as sess:
#     init.run()
#     for epoch in range(n_epochs):
#         for iteration in range(mnist.train.num_examples // batch_size):
#             X_batch, y_batch = mnist.train.next_batch(batch_size)
#             sess.run(training_op, feed_dict={X: X_batch, y: y_batch})
#         acc_train = accuracy.eval(feed_dict={X: X_batch, y: y_batch})
#         acc_test = accuracy.eval(
#             feed_dict={X: mnist.test.images,
#                        y: mnist.test.labels})
#         print(epoch, 'traing accuracy:', acc_train, 'test accuracy:', acc_test)
#     save_path = saver.save(sess, './my_model.ckpt')

with tf.Session() as sess:
    saver.restore(sess, "./my_model.ckpt")  # or better, use save_path
    X_new_scaled = mnist.test.images[:20]
    Z = logits.eval(feed_dict={X: X_new_scaled})
    y_pred = np.argmax(Z, axis=1)

print("Predicted classes:", y_pred)
print("Actual classes:   ", mnist.test.labels[:20])
