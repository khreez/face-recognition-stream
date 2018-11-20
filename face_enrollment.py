import os
import shutil
import argparse
import utils

from keras.preprocessing.image import ImageDataGenerator
from face_recognition import face_locations, load_image_file
from face_encoding import encode_faces
from tqdm import tqdm

MIN_SAMPLES_COUNT = 250

datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    fill_mode='nearest',
    horizontal_flip=True)


def enroll_faces():
    print('enrolling captured face image(s)')

    count = 0
    for label in _get_labels():
        label_dir = os.path.join(utils.CAPTURE_DIR, label)

        for image_file_name in os.listdir(label_dir):
            image_path = os.path.join(label_dir, image_file_name)
            _augment_image(image_path, label)
            _post_process(image_path)

    encode_faces()

    print('enrolled {} face image(s)'.format(count))


def enroll_face(image_path, label):
    _augment_image(image_path, label)
    _post_process(image_path)
    encode_faces()


def _augment_image(image_path, label):
    print('augmenting image: {} with label: {}'.format(image_path, label))
    target_dir = os.path.join(utils.TRAINING_DIR, label)
    _conditionally_create_dir(target_dir)

    augmented_sample_count = 0
    image_array = _process_image(image_path)
    if image_array is not None:
        print('storing augmentations in: {}'.format(target_dir))
        for _ in datagen.flow(image_array, batch_size=1, save_to_dir=target_dir, save_prefix=label, save_format='jpeg'):
            augmented_sample_count += 1
            if augmented_sample_count > MIN_SAMPLES_COUNT:
                break

    if augmented_sample_count > 0:
        print('generated {} augmented sample face image(s)'.format(augmented_sample_count))
    else:
        print('No augmented sample face image generated for: {}'.format(label))


def _get_labels():
    labels = []
    with os.scandir(utils.CAPTURE_DIR) as it:
        for entry in it:
            if entry.is_dir():
                labels.append(entry.name)
    return labels


def _process_image(image_path):
    margin = 65
    face_image = None
    image = load_image_file(image_path)
    if len(image):
        facial_locations = face_locations(image, model='cnn')
        if len(facial_locations):
            top, right, bottom, left = facial_locations[0]
            face_image = image[top - margin:bottom + margin, left - margin:right + margin]
            face_image = face_image.reshape((1,) + face_image.shape)
    return face_image


def _post_process(source_path):
    if os.path.exists(source_path):
        target_path = source_path.replace(utils.CAPTURE_DIR, utils.TRAINING_DIR)
        print('post-processing: {} moving to: {}'.format(source_path, target_path))
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copyfile(source_path, target_path)
        os.remove(source_path)


def _conditionally_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image", help="path to the input image")
    parser.add_argument("-l", "--label", help="label for the input image")

    args = vars(parser.parse_args())
    if args['image'] and args['label']:
        enroll_face(args['image'], args['label'])
    else:
        enroll_faces()
