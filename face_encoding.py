import pickle
import os
import shutil
import utils

from face_recognition import face_locations, face_encodings, load_image_file
from imutils import paths
from tqdm import tqdm


def encode_faces():
    print('encoding facial features')

    encodings = []
    labels = []
    for image_path in paths.list_images(utils.TRAINING_DIR):
        label = image_path.split(os.path.sep)[-2]
        labels.append(label)
        image_encodings = _process_face_encodings(image_path)
        encodings.extend(image_encodings)

    if len(encodings) and len(labels):
        _process_encodings(encodings, labels)
        _post_process()
    else:
        print('no face image(s) to encode')


def _process_face_encodings(image_path):
    print('processing facial encodings for {}'.format(image_path))

    image = load_image_file(image_path)
    facial_locations = face_locations(image, model='cnn')
    return face_encodings(image, facial_locations)


def _process_encodings(encodings, labels):
    if len(encodings) and len(labels):
        print('processing {} encoding(s) with label(s): {}'.format(len(encodings), labels))

        source_encodings, source_labels = utils.load_source_encodings()
        source_encodings.extend(encodings)
        source_labels.extend(labels)

        _serialize_encodings(source_encodings, source_labels)
    else:
        print('no encodings/labels found, nothing to process')


def _serialize_encodings(encodings, labels):
    if len(encodings) and len(labels):
        with open(utils.ENCODINGS_FILENAME, 'wb') as f:
            f.write(pickle.dumps({
                utils.ENCODINGS_KEY: encodings,
                utils.LABELS_KEY: labels
            }))
    else:
        print('empty encodings/labels, nothing to serialize')


def _post_process():
    for image_path in paths.list_images(utils.TRAINING_DIR):
        target_path = os.path.join(utils.VAULT_DIR, image_path)
        print('post-processing: {} moving to: {}'.format(image_path, target_path))
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copyfile(image_path, target_path)
        os.remove(image_path)


if __name__ == '__main__':
    encode_faces()
