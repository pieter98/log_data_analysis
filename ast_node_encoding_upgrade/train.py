import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import pickle
import logging
import tensorflow as tf
from ast_node_encoding_upgrade import network, sampling
import ast_node_encoding_upgrade.sampling
from database_connection import DatabaseConnection
from ast_node_encoding_upgrade.node_map import NODE_MAP
from ast_node_encoding_upgrade.constants import NUM_FEATURES, LEARN_RATE, BATCH_SIZE, EPOCHS, CHECKPOINT_EVERY
from tensorboard.plugins import projector
tf.compat.v1.disable_eager_execution()

def learn_vectors(samples, logdir, outfile, num_feats=NUM_FEATURES, epochs=EPOCHS):
    """Learn a vector representation of Python AST nodes."""

    # build the inputs and outputs of the network
    input_node, label_node, embed_node, loss_node = network.init_net(
        num_feat=num_feats,
        batch_size=BATCH_SIZE
    )
    

    # use gradient descent with momentum to minimize the training objective
    train_step = tf.compat.v1.train.GradientDescentOptimizer(LEARN_RATE).minimize(loss_node)
    

    tf.compat.v1.summary.scalar('loss', loss_node)

    ### init the graph
    sess = tf.compat.v1.Session()

    with tf.name_scope('saver'):
        saver = tf.compat.v1.train.Saver()
        summaries = tf.compat.v1.summary.merge_all()
        writer = tf.compat.v1.summary.FileWriter(logdir, sess.graph)
        config = projector.ProjectorConfig()
        embedding = config.embeddings.add()
        embedding.tensor_name = embed_node.name
        embedding.metadata_path = os.path.join('vectorizer', 'metadata.tsv')
        projector.visualize_embeddings(writer, config)

    sess.run(tf.compat.v1.global_variables_initializer())

    checkfile = os.path.join(logdir, 'ast2vec.ckpt')

    embed_file = open(outfile, 'wb')

    step = 0
    for epoch in range(1, 100+1):
        sample_gen = sampling.batch_samples(samples, BATCH_SIZE)
        for batch in sample_gen:
            input_batch, label_batch = batch

            _, summary, embed, err = sess.run(
                [train_step, summaries, embed_node, loss_node],
                feed_dict={
                    input_node: input_batch,
                    label_node: label_batch
                }
            )

            print('Epoch: ', epoch, 'Loss: ', err)
            writer.add_summary(summary, step)
            if step % CHECKPOINT_EVERY == 0:
                # save state so we can resume later
                saver.save(sess, os.path.join(checkfile), step)
                print('Checkpoint saved.')
                # save embeddings
                pickle.dump((embed, NODE_MAP), embed_file)
            step += 1
            
        

    # save embeddings and the mapping
    pickle.dump((embed, NODE_MAP), embed_file)
    embed_file.close()
    saver.save(sess, os.path.join(checkfile), step)


def train():
    
    # with open("./ast_node_encoding_upgrade/data/algorithm_nodes.pkl", "rb") as sample_file:
    #     samples = pickle.load(sample_file)
    conn = DatabaseConnection()
    samples = conn.get_generated_simple_data_dataset()
    
   
    # if args.model.lower() == 'ast2vec':
    learn_vectors(samples, "logs/algorithm", "./ast_node_encoding_upgrade/data/vectors.pkl")

