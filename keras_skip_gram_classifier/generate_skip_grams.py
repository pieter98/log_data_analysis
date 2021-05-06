import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import io
import re
import string
import tensorflow as tf
from tqdm import tqdm

from constants import NUM_NEG
from tensorflow.keras import Model
from tensorflow.keras.layers import Dot, Embedding, Flatten
from tensorflow.keras.layers.experimental.preprocessing import TextVectorization

from database_connection import DatabaseConnection

SEED = 42
AUTOTUNE = tf.data.experimental.AUTOTUNE

def define_vocab(samples):
    vocab, index = {}, 1 # start from index 1
    vocab[''] = 0 # add a padding token
    print("define vocab")
    for sample in tqdm(samples):
        if (sample["node"] not in vocab):
            vocab[sample["node"]] = index
            index += 1
        
        for child in sample["children"]:
            if (child not in vocab):
                vocab[child] = index
                index += 1

        if (sample["parent"] not in vocab):
            vocab[sample["parent"]] = index
            index += 1
    
    inverse_vocab = {index: token for token, index in vocab.items()}
    return vocab, inverse_vocab


def transform_samples_to_sequences(samples, vocab):
    sequences = []
    for sample in samples:
        tokens = [sample["parent"]] + [sample["node"]]         
        sequence = [vocab[token] for token in tokens]
        # if len(sequence) < 10:
        #     for i in range(len(sequence),10):
        #         sequence.append(0)
        # elif len(sequence) > 10:
        #     sequence = sequence[:10]
        sequences.append(sequence)

    return sequences

def transform_samples_to_sequences_with_children(samples, vocab):
    sequences = []
    for sample in samples:
        tokens = [sample["parent"]] + [sample["node"]] + sample["children"]    
        sequence = [vocab[token] for token in tokens if token != None]
        # if len(sequence) < 10:
        #     for i in range(len(sequence),10):
        #         sequence.append(0)
        # elif len(sequence) > 10:
        #     sequence = sequence[:10]
        sequences.append(sequence)

    return sequences




# Generates skip-gram pairs with negative sampling for a list of sequences
# (int-encoded sentences) based on window size, number of negative samples
# and vocabulary size.
def generate_training_data(sequences, window_size, vocab_size, seed, num_ns=NUM_NEG):
  # Elements of each training example are appended to these lists.
  targets, contexts, labels = [], [], []

  # Build the sampling table for vocab_size tokens.
  sampling_table = tf.keras.preprocessing.sequence.make_sampling_table(vocab_size)

  # Iterate over all sequences (sentences) in dataset.
  for sequence in tqdm(sequences):

    # Generate positive skip-gram pairs for a sequence (sentence).
    positive_skip_grams, _ = tf.keras.preprocessing.sequence.skipgrams(
          sequence,
          vocabulary_size=vocab_size,
          sampling_table=sampling_table,
          window_size=window_size,
          negative_samples=0)

    # Iterate over each positive skip-gram pair to produce training examples
    # with positive context word and negative samples.
    for target_word, context_word in positive_skip_grams:
      context_class = tf.expand_dims(
          tf.constant([context_word], dtype="int64"), 1)
      negative_sampling_candidates, _, _ = tf.random.log_uniform_candidate_sampler(
          true_classes=context_class,
          num_true=1,
          num_sampled=num_ns,
          unique=True,
          range_max=vocab_size,
          seed=SEED,
          name="negative_sampling")

      # Build context and label vectors (for one target word)
      negative_sampling_candidates = tf.expand_dims(
          negative_sampling_candidates, 1)

      context = tf.concat([context_class, negative_sampling_candidates], 0)
      label = tf.constant([1] + [0]*num_ns, dtype="int64")

      # Append each element from the training example to global lists.
      targets.append(target_word)
      contexts.append(context)
      labels.append(label)

  return targets, contexts, labels

