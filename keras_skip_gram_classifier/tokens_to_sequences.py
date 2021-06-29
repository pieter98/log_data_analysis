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
    for sample in tqdm(samples, desc="SAMPLES > TOKENS"):
        tokens = [sample["parent"]] + [sample["node"]] + sample["children"]    
        sequence = [vocab[token] for token in tokens if token != None]
        # if len(sequence) < 10:
        #     for i in range(len(sequence),10):
        #         sequence.append(0)
        # elif len(sequence) > 10:
        #     sequence = sequence[:10]
        sequences.append(sequence)

    return sequences

def transform_random_walks_to_sequences(walks,vocab):
    sequences = []
    for walk in tqdm(walks, desc="WALKS > TOKENS"):
        sequence = [vocab[token] for token in walk]
        sequences.append(sequence)

    return sequences