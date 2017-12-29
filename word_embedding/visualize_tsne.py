# -*- coding: utf-8 -*-
from gensim.models import KeyedVectors
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import pandas as pd
import logging
import os
import argparse
from word2vec2tensor import word2vec2tensor
from subprocess import call

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

# load model
phrase_filename = '/home/weiwu/share/deep_learning/data/model/phrase/enwiki_economy/word2vec_org'
finance_level5_model_filepath = '/home/weiwu/share/deep_learning/data/model/phrase/word2vec_org_finance_level_5'
# model_level5 = KeyedVectors.load_word2vec_format(phrase_filename, binary=False)
logger.debug('loading model completes.')

finance_vocab = [
    'sales',
    'gdp',
    'sales',
    'revenue',
    'growth_rate',
    'net_income',
    'cash_flow',
    'debt',
    'assets',
    'dividend_yield',
    'llc',
    'ltd',
    'company',
    'firm',
    'earnings',
    'book_value',
    'interest_rate',
    'dividend',
    'information_ratio',
    'tracking',
    'risk',
    'return',
    'excess_return',
    'active_return',
    'profit',
    'pv',
    'fv',
    'capm',
    'arbitrage',
    'efficient',
    'alpha',
    'beta',
    'sigma',
    'omega',
    'greek',
    'future',
    'option',
    'maturaty',
    'pay_off',
    'sharpe_ratio'
    'rate_of_return',
    'yield',
    'net_income',
    'portfolio',
    'value',
]

# topn = 20

# # read all pages title
# pages_csv = pd.DataFrame()
# for root, dirs, files in os.walk(
#         '/home/weiwu/share/deep_learning/data/enwiki_categories/'):
#     for filename in files:
#         file_path = root + '/' + filename
#         page_read = pd.read_csv(
#             file_path,
#             dtype={'title': str},
#             converters={'title': lambda x: x.lower()})
#         pages_csv = pd.concat([pages_csv, page_read])
# ls_page_title = pages_csv.title.unique()


# # get all finance vocabulary
# all_finance_vocab = ls_page_title.tolist()
def complete_dir_path(dir_path):
    if not dir_path.endswith('/'):
        return dir_path + '/'
    else:
        return dir_path


def word2vec2tsv(word2vec_model_path, tensor_filename, vocab=[], binary=False):
    """only visualize input vocab
    Keyword Arguments:
    model --
    vocab --
    """
    from gensim.utils import to_utf8
    model = KeyedVectors.load_word2vec_format(
        word2vec_model_path, binary=binary)
    if not os.path.exists(tensor_filename):
        logger.debug("create dir %s" % tensor_filename)
        os.makedirs(tensor_filename)

    outfiletsv = complete_dir_path(tensor_filename) + 'tensor.tsv'
    outfiletsvmeta = complete_dir_path(tensor_filename) + 'metadata.tsv'

    if len(vocab) != 0:
        abs_vocab = []
        # remove absent vocabulary
        for token in vocab:
            if token not in model:
                #         logger.debug('pop %s' % vocab)
                abs_vocab.append(token)
                vocab.remove(token)
        logger.debug("absent vocabulary in the model %s" % abs_vocab)
    else:
        vocab = model.index2word

    # write tensor value
    with open(outfiletsv, 'w+') as file_vector:
        with open(outfiletsvmeta, 'w+') as file_metadata:
            for word in vocab:
                file_metadata.write(to_utf8(word) + to_utf8('\n'))
                vector_row = '\t'.join(str(x) for x in model[word])
                file_vector.write(vector_row + '\n')


def visualize_embedding_tsne(model, vocab):
    """tsne word embedding
    Keyword Arguments:
    model -- gensim embedding model
    vocab -- list of vocab to display
    """
    # get vocabulary dictionary
    dict_vocab = model.wv.vocab
    logger.debug('extracting vocabulary completes.')

    # get finance vocabulary dictionary
    sub_dict_vocab = {}
    for key in vocab:
        sub_dict_vocab[key] = dict_vocab.get(key)

    # remove absent vocabulary
    for vocab in sub_dict_vocab.keys():
        if vocab not in model:
            #         logger.debug('pop %s' % vocab)
            sub_dict_vocab.pop(vocab, None)
    # index the model, you can be sure that you know the order of the words.
    idx_vocab = list(sub_dict_vocab)
    # gets you a standalone vocab list for the final dataframe to plot
    X = model[sub_dict_vocab]
    tsne = TSNE(n_components=2)
    X_tsne = tsne.fit_transform(X)
    logger.debug("transforming completes")
    # plt.scatter(X_tsne[:, 0], X_tsne[:, 1])
    # plt.show()
    df = pd.DataFrame(X_tsne, index=idx_vocab, columns=['x', 'y'])

    # plot figure
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)

    ax.scatter(df['x'], df['y'])
    for word, pos in df.iterrows():
        ax.annotate(word, pos)
    plt.show()


def visualize_embedding_tensorboard_projector(LOG_DIR,
                                              host="localhost",
                                              model_path=phrase_filename,
                                              call_tensorboard=False):
    """
    1. setup a 2d tensor that holds embedding(s).
    2. periodically save model variables in a checkpoint in LOG_DIR.
    3. (optional) associate medadata with embedding
    Keyword Arguments:
    save_path  --
    model_path --
    """
    import tensorflow as tf
    from tensorflow.contrib.tensorboard.plugins import projector
    if not LOG_DIR:
        if not os.path.exists("./LOG_DIR"):
            os.makedirs("./LOG_DIR")
    else:
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)
    # Create randomly initialized embedding weights which will be trained.
    N = 10000  # Number of items (vocab size).
    D = 200  # Dimensionality of the embedding.
    with tf.Graph().as_default() as g:
        with tf.Session(graph=g) as session:
            summary_writer = tf.summary.FileWriter(LOG_DIR)
            embedding_var = tf.Variable(
                tf.random_normal([N, D]), name='word_embedding')
            init = tf.initialize_all_variables()
            init.run()
            saver = tf.train.Saver()
            saver.save(session, os.path.join(LOG_DIR, "model.ckpt"), 0)
            # Format: tensorflow/contrib/tensorboard/plugins/projector/projector_config.proto
            config = projector.ProjectorConfig()
            embedding = config.embeddings.add()
            embedding.tensor_name = embedding_var.name
            embedding.metadata_path = os.path.join(LOG_DIR, 'metadata.tsv')
            projector.visualize_embeddings(summary_writer, config)

    if call_tensorboard:
        call(["tensorboard", "--logdir={}".format(LOG_DIR), "--host=%s" % host])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", required=False, help="Input word2vec model")
    parser.add_argument(
        "-o", "--output", required=False, help="Output tensor file name prefix")
    parser.add_argument(
        "-b",
        "--binary",
        required=False,
        help="If word2vec model in binary format, set True, else False")
    parser.add_argument(
        "-l",
        "--logdir",
        required=False,
        help="periodically save model variables in a checkpoint")
    parser.add_argument(
        "--host",
        required=False,
        help="host where holding the tensorboard projector service")
    parser.add_argument("-p", "--port", required=False, help="browser port")
    args = parser.parse_args()

    # word2vec2tsv(finance_level5_model_filepath,"/home/weiwu/share/deep_learning/data/model/phrase/finance_level_5/part_vocab",finance_vocab)
    # word2vec2tensor(args.input, args.output, args.binary)
    visualize_embedding_tensorboard_projector(
        args.logdir, args.host, model_path=args.input, call_tensorboard=False)
#    visualize_embedding(model_level5, finance_vocab)
