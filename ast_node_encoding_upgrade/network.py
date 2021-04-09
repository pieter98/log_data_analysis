import math
import tensorflow as tf

from node_map import NODE_MAP
from constants import BATCH_SIZE, NUM_FEATURES, HIDDEN_NODES
tf.compat.v1.disable_eager_execution()

def init_net(batch_size=BATCH_SIZE, num_feat=NUM_FEATURES, hidden_size=HIDDEN_NODES):
    with tf.name_scope('network'):

        with tf.name_scope('inputs'):
            # input node-child pairs
            inputs = tf.compat.v1.placeholder(tf.int32, shape=[batch_size,], name='inputs')
            labels = tf.compat.v1.placeholder(tf.int32, shape=[batch_size,], name='labels')

            # embeddings to learn
            embeddings = tf.compat.v1.Variable(
                tf.compat.v1.random_uniform([len(NODE_MAP), num_feat]),
                name='embeddings'
            )

            embed = tf.compat.v1.nn.embedding_lookup(embeddings, inputs)
            onehot_labels = tf.compat.v1.one_hot(labels, len(NODE_MAP), dtype=tf.float32)

        # weights will have features on the rows and nodes on the columns
        with tf.name_scope('hidden'):
            weights = tf.compat.v1.Variable(
                tf.compat.v1.truncated_normal(
                    [num_feat, hidden_size], stddev=1.0 / math.sqrt(num_feat)
                ),
                name='weights'
            )

            biases = tf.compat.v1.Variable(
                tf.zeros((hidden_size,)),
                name='biases'
            )

            hidden = tf.compat.v1.tanh(tf.matmul(embed, weights) + biases)

        with tf.name_scope('softmax'):
            weights = tf.compat.v1.Variable(
                tf.compat.v1.truncated_normal(
                    [hidden_size, len(NODE_MAP)],
                    stddev=1.0 / math.sqrt(hidden_size)
                ),
                name='weights'
            )
            biases = tf.Variable(
                tf.zeros((len(NODE_MAP),), name='biases')
            )

            logits = tf.matmul(hidden, weights) + biases

        with tf.name_scope('error'):
            cross_entropy = tf.nn.softmax_cross_entropy_with_logits(
                labels=onehot_labels, logits=logits, name='cross_entropy'
            )

            loss = tf.compat.v1.reduce_mean(cross_entropy, name='cross_entropy_mean')

    return inputs, labels, embeddings, loss

init_net()