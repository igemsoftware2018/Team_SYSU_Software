import tensorflow as tf
import numpy as np
import pandas as pd


learning_rate = 0.001
training_epochs = 4000
batch_size = 256
n_input = 300 
n_hidden_1 = 256 
n_hidden_2 = 128
n_hidden_3 = 64
display_step = 1


X = tf.placeholder(tf.float32, [None,n_input], name = 'X')

weights = {
    'w1':tf.Variable(tf.random_normal([n_input,n_hidden_1]), name='w1'),
    'w2': tf.Variable(tf.random_normal([n_hidden_1,n_hidden_2]), name='w2'),
    'w3': tf.Variable(tf.random_normal([n_hidden_2,n_hidden_3]), name='w3'),
    }

biases = {
    'b1': tf.Variable(tf.random_normal([n_hidden_1]), name='b1'),
    'b2': tf.Variable(tf.random_normal([n_hidden_2]), name='b2'),
    'b3': tf.Variable(tf.random_normal([n_hidden_3]), name='b3'),
    }

saver = tf.train.Saver()


def nuralnetwork(x):
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['w1']),
                                   biases['b1']))
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['w2']),
                                   biases['b2']))
    layer_3 = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['w3']),
                                   biases['b3']), name = 'net_output')
    return layer_3

net_output = nuralnetwork(X)
y_pred = net_output
y = tf.placeholder(tf.float32, [None, 64])

cost = tf.reduce_mean(tf.pow(y - y_pred, 2))
optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost)

word_ = pd.read_csv('wordVec.csv', header = None)
word_vector = np.array(word_)

team_ = pd.read_csv('team_features.csv', header = None)
team_features = np.array(team_)


with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    total_batch = int(len(word_vector)/batch_size)
    #train begin
    for epoch in range(training_epochs):
        for i in range(total_batch):
            batch_xs = word_vector[i*batch_size:(i+1)*batch_size]
            batch_ys = team_features[i*batch_size:(i+1)*batch_size]
            _, c = sess.run([optimizer, cost], feed_dict={X: batch_xs, y: batch_ys})
        if epoch % display_step == 0:
            print("Epoch:", '%04d' % (epoch+1),
                  "cost=", "{:.9f}".format(c))
    #save the model
    saver.save(sess, './checkpoint_dir1/MyModel', global_step = 4000)
    print("Save the model!")
    print("Optimization Finished!")
    #test
    print(sess.run(y_pred, feed_dict = {X: [word_vector[2]]}))
