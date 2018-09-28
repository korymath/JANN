import os
import sys
import random
import argparse
import tensorflow as tf
import sentencepiece as spm
import tensorflow_hub as hub
from annoy import AnnoyIndex
from utils import GenModelUSE, MODULE_PATH, process_to_IDs_in_sparse_format

# set the tfhub cache dir explicitly
os.environ["TFHUB_CACHE_DIR"] = "data/module"


def main(arguments):
  parser = argparse.ArgumentParser(
      description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('--verbose', dest='verbose',
                      help="Verbose", action='store_true')
  parser.add_argument('--num_neighbors', type=int,
    help='number of nearest neighbors to return')
  parser.add_argument('--search_k', type=int,
    help='runtime tradeoff between accuracy and speed')
  parser.add_argument('--path_to_text',
    help="path to original text file")

  parser.set_defaults(
    verbose=True,
    num_neighbors=10,
    search_k=100
  )
  args = parser.parse_args(arguments)

  # Reduce logging output.
  if args.verbose:
    tf.logging.set_verbosity(tf.logging.DEBUG)
  else:
    tf.logging.set_verbosity(tf.logging.INFO)

  tf.logging.info('Loading unique strings.')

  DATA_PATH = args.path_to_text
  UNIQUE_STRINGS_PATH = DATA_PATH + '.embedded.pkl_unique_strings.csv'
  # load the unique lines
  with open(UNIQUE_STRINGS_PATH) as f:
      UNIQUE_STRINGS = [line.rstrip() for line in f]

  tf.logging.info('Lodaded {} unique strings'.format(len(UNIQUE_STRINGS)))

  # define the path of the nearest neighbor model to use
  ANNOY_INDEX_PATH = DATA_PATH + '.ann'

  # Load generative models from pickles to generate from scratch.
  try:
    tf.logging.info('Build generative model...')
    GEN_MODEL_USE = GenModelUSE(
      annoy_index_path=ANNOY_INDEX_PATH,
      unique_strings=UNIQUE_STRINGS
    )
    tf.logging.info('Generative model built.')
  except (OSError, IOError) as e:
    tf.logging.info('Error building generative model.')

  # build a loop for interactive mode
  while True:
    # get user input
    user_input = input('\nQuery Text: ')
    # if user input is too short
    if len(user_input) < 1:
      continue
    resp = GEN_MODEL_USE.inference(user_input)
    tf.logging.info('{}'.format(resp))

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))









