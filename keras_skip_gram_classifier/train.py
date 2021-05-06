import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import io

from database_connection import DatabaseConnection

from generate_skip_grams import define_vocab, transform_samples_to_sequences, generate_training_data
from batching_performance import configure_dataset_for_performance
from tensorboard.plugins import projector
from model import *
from constants import *

SEED = 42

conn = DatabaseConnection()
samples = conn.get_generated_simple_data_dataset()
vocab, inverse_vocab = define_vocab(samples)
sequences = transform_samples_to_sequences(samples, vocab)
targets, contexts, labels = generate_training_data(sequences, 2, len(vocab), SEED)

dataset = configure_dataset_for_performance(targets, contexts, labels)

print(f"targets: {len(targets)}")
print(f"contexts: {len(contexts)}")
print(f"labels: {len(labels)}")


# build model
node2vec = Node2Vec(len(vocab))
node2vec.compile(
    optimizer='adam',
    loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)

tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir="logs")

node2vec.fit(dataset, epochs=20, callbacks=[tensorboard_callback])



weights = node2vec.get_layer('n2v_embedding').get_weights()[0]

log_dir = f'skip_gram_results/{DIR_NAME}/'
if not os.path.exists(log_dir):
  os.makedirs(log_dir)
out_v = io.open(os.path.join(log_dir,'vectors.tsv'), 'w', encoding='utf-8')
out_m = io.open(os.path.join(log_dir,'metadata.tsv'), 'w', encoding='utf-8')

for index, word in enumerate(vocab):
  if index == 0 or word == None:
    continue  # skip 0, it's padding.
  vec = weights[index]
  out_v.write('\t'.join([str(x) for x in vec]) + "\n")
  out_m.write(word + "\n")
out_v.close()
out_m.close()