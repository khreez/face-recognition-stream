import os
import pickle

CAPTURE_DIR = 'capture'
TRAINING_DIR = 'training'
VAULT_DIR = 'vault'
ENCODINGS_DIR = 'encodings'

ENCODINGS_FILENAME = ENCODINGS_DIR + '/encoded_faces.pickle'
ENCODINGS_KEY = 'encodings'
LABELS_KEY = 'names'


def load_source_encodings():
    if not os.path.exists(ENCODINGS_FILENAME):
        return [], []

    with open(ENCODINGS_FILENAME, 'rb') as f:
        data = pickle.loads(f.read())
        source_encodings = data[ENCODINGS_KEY]
        source_labels = data[LABELS_KEY]

    if len(source_encodings) and len(source_labels):
        return source_encodings, source_labels
    else:
        return [], []
