import tensorflow as tf

DIR_NAME = 'attempt9'
BATCH_SIZE = 1024
BUFFER_SIZE = 10000
AUTOTUNE = tf.data.experimental.AUTOTUNE
NUM_NEG = 4
EMBEDDING_DIM = 30