""" Run LDA topic model on Dataset and save results to JSON and analysis
file."""

import imp
settings = imp.load_source('module.name', 'nsweb/initializers/settings.py')
# from nsweb.initializers import settings
from neurosynth.base.dataset import Dataset
from subprocess import call, check_output
import os
import re
import numpy as np
import pandas as pd
import tempfile
import json

# Path to Mallet binary on local system
MALLET_PATH = '/usr/local/mallet/bin/mallet'
# Path to file containing all abstracts
ABSTRACT_PATH = os.path.join(settings.ASSET_DIR, 'abstracts.txt')
# Path to extra stopword list (set to None to disable)
STOPWORDS = os.path.join(settings.ASSET_DIR, 'misc', 'stopwords.txt')


class Mallet:

    def __init__(self, working_dir=None, mallet_path=None):
        if working_dir is None:
            working_dir = tempfile.mkdtemp()
        os.chdir(working_dir)

    def import_file(self, input, output, extra_stopwords=None):
        line = MALLET_PATH + ' import-file --input %s --output %s --keep-sequence --remove-stopwords' % (input, output)
        if extra_stopwords is not None:
            line += ' --extra-stopwords %s' % extra_stopwords
        res = check_output(line.split())
        self.corpus = output
        return res

    def import_dir(self, input, output, extra_stopwords=None):
        line = MALLET_PATH + ' import-dir --input %s --output %s --keep-sequence --remove-stopwords' % (input, output)
        if extra_stopwords is not None:
            line += ' --extra-stopwords %s' % extra_stopwords
        res = check_output(line.split())
        self.corpus = output
        return res

    def train_topics(self, input=None, num_topics=100, optimize_interval=10,
                     output_doc_topics='doc_topics.txt', output_topic_keys='topic_keys.txt', 
                     output_model=None, num_top_words=20, inferencer_filename=None, num_threads=None,
                     num_iterations=None):
        if input is None:
            input = self.corpus
        line = MALLET_PATH + ' train-topics --input %s --num-topics %d' % (input, num_topics)
        args = locals()
        for p in ['optimize_interval', 'output_doc_topics', 'output_topic_keys', 
                    'output_model', 'num_top_words', 'inferencer_filename', 'num_threads',
                    'num_iterations']:
            if p in args and args[p] is not None:
                line += ' --%s %s' % (p.replace('_', '-'), str(args[p]))
        self.doc_topics = output_doc_topics
        return check_output(line.split())

    def parse_doc_topics(self, input=None, prefix=''):
        ''' Reads in a doc-topics MALLET file produced by train-topics and 
        rearranges it into a pandas DF where the rows are documents and 
        the columns are topics in natural order. '''
        if input is not None:
            self.doc_topics = input
        docs = open(self.doc_topics).readlines()[1::]

        n_topics = len(docs[0].strip().split('\t'))/2 - 1
        n_docs = len(docs)
        labels = []

        print "Found %d documents and %d topics. Reordering weights..." % (n_docs, n_topics)

        weights = np.zeros((n_docs, n_topics))

        # Loop over doc_topics lines
        for i, line in enumerate(docs):

            # Zip through pairs and create an ordered list of weights
            l = line.strip().split('\t')
            labels.append(l[1])
            raw_vals = l[2::]

            pairs = zip(raw_vals[0::2], raw_vals[1::2])
            for p in pairs:
                weights[i, int(p[0])] = p[1]

        columns = [prefix + str(i) for i in range(n_topics)]
        return pd.DataFrame(weights, index=labels, columns=columns)


class TopicFactory(object):

    def __init__(self, dataset=None, corpus=None):

        # if dataset is None:
        #     dataset = Dataset.load(settings.PICKLE_DATABASE)
        # self.dataset = dataset

        if corpus is None:
            corpus = ABSTRACT_PATH
        self.corpus = corpus

        self.mallet = Mallet()
        self.mallet.import_file(
            ABSTRACT_PATH, 'texts.mallet', extra_stopwords=STOPWORDS)

    def make_topics(self, n_topics):

        if isinstance(n_topics, int):
            n_topics = [n_topics]

        analysis_dir = os.path.join(settings.TOPIC_DIR, 'analyses')
        if not os.path.exists(analysis_dir):
            os.makedirs(analysis_dir)

        key_dir = os.path.join(settings.TOPIC_DIR, 'keys')
        if not os.path.exists(key_dir):
            os.makedirs(key_dir)

        for n in n_topics:
            key_file = os.path.join(key_dir, 'topics_%d.txt' % n)
            self.mallet.train_topics(
                'texts.mallet', num_topics=n, num_top_words=100,
                output_topic_keys=key_file, num_iterations=1000)
            topics = self.mallet.parse_doc_topics(prefix='topic')
            topic_file = os.path.join(analysis_dir,
                                      'topics_%d.txt' % n)
            topics.to_csv(topic_file, sep='\t', index_label='id')

            # Write json file
            name = 'v3-topics-%d' % int(n)
            metadata = {
                'name': name,
                'description': 'A set of %d topics extracted with LDA from '
                'the abstracts of all articles in the Neurosynth database as of'
                ' February 2015 (10,903 articles).' % n,
                'n_topics': n
            }
            json_file = os.path.join(settings.TOPIC_DIR, name + '.json')
            open(json_file, 'w').write(json.dumps(metadata))

if __name__ == '__main__':
    tf = TopicFactory()
    tf.make_topics([50, 100, 200])