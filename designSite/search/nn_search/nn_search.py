

import os

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.neighbors import BallTree

currentPath = os.path.dirname(os.path.realpath(__file__))
wordVecFile = os.path.join(currentPath, 'wordVectors.bin')
keyword_matrix_2018_filename = os.path.join(currentPath, "keyword_matrix_2018.csv")
checkPointPath = os.path.join(currentPath, 'checkpoint')
team_features_filename = os.path.join(currentPath, 'team_features.csv')
checkPointData = os.path.join(checkPointPath, 'model.meta')

class Word2Vec(object):
    def __init__(self, fname=wordVecFile):
        word_vecs = {}
        with open(fname, "rb") as f:
            header = f.readline()
            vocab_size, layer1_size = map(int, header.split()) # 3000000 300
            binary_len = np.dtype('float32').itemsize * layer1_size # 1200
            for line in range(vocab_size):
                words = []
                while True:
                    ch = f.read(1)
                    if ch == '\xc2':
                        words = ''
                        break
                    if ch == ' ' or len(ch.strip()) == 0:
                        words = ''.join(words)
                        break
                    if ch != '\n':
                        words.append(str(ch))
                word_vecs[words] = np.fromstring(f.read(binary_len), dtype='float32')
        self.word_vecs = word_vecs
        self.flag = True

    def getWordVector(self, word):
        if word.lower() not in self.word_vecs:
            return np.random.uniform(-0.25, 0.25, 300)
        else:
            return self.word_vecs[word]

def recommend_team(word,k=10):
    if not recommend_team.init:
        print(keyword_matrix_2018_filename)
        recommend_team.data = np.array(pd.read_csv(keyword_matrix_2018_filename, header = None)) 
        print("Loading Word Vector...")
        recommend_team.word2vec = Word2Vec()
        recommend_team.word_vector = recommend_team.word2vec.getWordVector(word)
        recommend_team.init = True
        print("Finish loading.")
    res = []
    with tf.Session() as sess:
        #load the model
        saver = tf.train.import_meta_graph(checkPointData)
        saver.restore(sess, tf.train.latest_checkpoint(checkPointPath))
        graph = tf.get_default_graph()
        y = graph.get_tensor_by_name("net_output:0")
        x = graph.get_tensor_by_name("X:0")
        feature = sess.run(y, feed_dict = {x: [recommend_team.word_vector]})
        team_features = np.array(pd.read_csv(team_features_filename, header = None))
        tree = BallTree(team_features, leaf_size=40)
        dist, ind = tree.query(feature, k=10)
        for i in ind:
            res.append({'team_name': recommend_team.data[i,0], 'year': recommend_team.data[i,1], 'link': recommend_team.data[i,2]})
    return res
recommend_team.init = False
recommend_team.data = None
recommend_team.word2vec = None
recommend_team.word_vector = None


# print(recommend_team("cancer"))
