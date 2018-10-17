import tensorflow as tf
import numpy as np
import pandas as pd

learning_rate = 0.01
training_epochs = 200
batch_size = 256

n_input = 1021 
n_hidden_1 = 512 
n_hidden_2 = 256 
n_hidden_3 = 64  
display_step = 1


X = tf.placeholder(tf.float32, [None,n_input], name = 'x')
 
weights = {
    'encoder_h1':tf.Variable(tf.random_normal([n_input,n_hidden_1]), name='encoder_h1'),
    'encoder_h2': tf.Variable(tf.random_normal([n_hidden_1,n_hidden_2]), name='encoder_h2'),
    'encoder_h3': tf.Variable(tf.random_normal([n_hidden_2,n_hidden_3]), name='encoder_h3'),
    'decoder_h1': tf.Variable(tf.random_normal([n_hidden_3,n_hidden_2]), name='decoder_h1'),
    'decoder_h2': tf.Variable(tf.random_normal([n_hidden_2,n_hidden_1]), name='decoder_h1'),
    'decoder_h3': tf.Variable(tf.random_normal([n_hidden_1, n_input]), name='decoder_h3'),
    }
biases = {
    'encoder_b1': tf.Variable(tf.random_normal([n_hidden_1]), name='encoder_b1'),
    'encoder_b2': tf.Variable(tf.random_normal([n_hidden_2]), name='encoder_b2'),
    'encoder_b3': tf.Variable(tf.random_normal([n_hidden_3]), name='encoder_b3'),
    'decoder_b1': tf.Variable(tf.random_normal([n_hidden_2]), name='encoder_b1'),
    'decoder_b2': tf.Variable(tf.random_normal([n_hidden_1]), name='encoder_b2'),
    'decoder_b3': tf.Variable(tf.random_normal([n_input]), name='encoder_b3'),
    }

saver = tf.train.Saver()

 
#encoder
def encoder(x):
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['encoder_h1']),
                                   biases['encoder_b1']))
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['encoder_h2']),
                                   biases['encoder_b2']))
    layer_3 = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['encoder_h3']),
                                   biases['encoder_b3']), name = 'encode_output')
    return layer_3
     
#decoder
def decoder(x):
    layer_1 = tf.nn.sigmoid(tf.add(tf.matmul(x, weights['decoder_h1']),
                                   biases['decoder_b1']))
    layer_2 = tf.nn.sigmoid(tf.add(tf.matmul(layer_1, weights['decoder_h2']),
                                   biases['decoder_b2']))
    layer_3 = tf.nn.sigmoid(tf.add(tf.matmul(layer_2, weights['decoder_h3']),
                                   biases['decoder_b3']), name = 'decode_output')
    return layer_3

#model
encoder_op = encoder(X)             
decoder_op = decoder(encoder_op)    
 
#loss
y_pred = decoder_op    
y_true = X            
cost = tf.reduce_mean(tf.pow(y_true - y_pred, 2))
optimizer = tf.train.AdamOptimizer(learning_rate).minimize(cost)


#training 
#load data
data = pd.read_csv('keyword_matrix_2018 2.csv',header = None)
data_input = np.array(data)[:,3:]

with tf.Session() as sess:
    sess.run(tf.global_variables_initializer())
    total_batch = int(len(data_input)/batch_size)
    #train begin
    for epoch in range(training_epochs):
        for i in range(total_batch):
            batch_xs = data_input[i*batch_size:(i+1)*batch_size]
            _, c = sess.run([optimizer, cost], feed_dict={X: batch_xs})
        if epoch % display_step == 0:
            print("Epoch:", '%04d' % (epoch+1),
                  "cost=", "{:.9f}".format(c))
    #save the model
    saver.save(sess, './checkpoint_dir/MyModel', global_step = 200)
    print("Save the model!")
    print("Optimization Finished!")
    writer = tf.summary.FileWriter("./checkpoint_dir/MyModel/tensorflow", tf.get_default_graph())
    writer.close()