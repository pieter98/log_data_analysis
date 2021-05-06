import io
import re
import string
import tensorflow as tf

from constants import NUM_NEG, EMBEDDING_DIM
from tensorflow.keras import Model
from tensorflow.keras.layers import Dot, Embedding, Flatten
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

class Node2Vec(Model):
    def __init__(self, vocab_size,num_neg=NUM_NEG, embedding_dim=EMBEDDING_DIM):
        super(Node2Vec, self).__init__()
        # layer which looks up the embedding of a node when it appears as a target word
        self.target_embedding = Embedding(vocab_size, embedding_dim, input_length=1, name="n2v_embedding")
        # layer which looks up the embedding of a node when it appears as a context word
        self.context_embedding = Embedding(vocab_size, embedding_dim, input_length=num_neg+1)
        # layer that computes the dot product of target and context embeddings from a training pair
        self.dots = Dot(axes=(3,2))
        # layer to flatten the results of dots layer into logits
        self.flatten = Flatten()

    def call(self, pair):
        target, context = pair
        word_emb = self.target_embedding(target)
        context_emb = self.context_embedding(context)
        dots = self.dots([context_emb, word_emb])
        return self.flatten(dots)

def custom_loss(x_logit, y_true):
    return tf.nn.sigmoid_cross_entropy_with_logits(logits=x_logit, labels=y_true)