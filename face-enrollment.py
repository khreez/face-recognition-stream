import os
import shutil

from datetime import datetime
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tqdm import tqdm

CAPTURE_DIR = 'capture'
AUGMENTED_DIR = 'augmented'
VAULT_DIR = 'vault'

datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    fill_mode='nearest',
    horizontal_flip=True)


def process_face_captures():
    print('Processing capture face image(s)')

    for label in get_labels():
        print('Processing captured image(s) for label: {}'.format(label))

        label_dir = os.path.join(CAPTURE_DIR, label)

        for image_file_name in tqdm(os.listdir(label_dir)):
            image_path = os.path.join(label_dir, image_file_name)
            generate_facial_augmentation(image_path, label)


def generate_facial_augmentation(image_path, label):
    target_dir = os.path.join(AUGMENTED_DIR, label)
    conditionally_create_dir(target_dir)

    augmented_sample_count = 0
    image_array = process_image(image_path)
    if image_array is not None:
        print('Processing image file: {} into: {}'.format(image_path, target_dir))
        prefix = '{}-{:%Y%m%d%H%M%S%f}'.format(label, datetime.utcnow())
        for _ in datagen.flow(image_array, batch_size=1, save_to_dir=target_dir, save_prefix=prefix,
                              save_format='jpeg'):
            augmented_sample_count += 1
            if augmented_sample_count > 1:  # 500
                break

    if augmented_sample_count > 0:
        print('Generated {} augmented sample face image(s) for: {} in {}'.format(augmented_sample_count, label,
                                                                                 target_dir))
        post_process(image_path)
    else:
        print('No augmented sample face image generated for: {}'.format(label))


def get_labels():
    labels = []
    with os.scandir(CAPTURE_DIR) as it:
        for entry in it:
            if entry.is_dir(): labels.append(entry.name)
    return labels


def process_image(image_path):
    result = None
    if image_path.endswith('.jpg'):
        image = load_img(image_path)
        # capture face area and store that in augmentation instead of orig image
        image_array = img_to_array(image)
        result = image_array.reshape((1,) + image_array.shape)
    return result


def post_process(source_path):
    target_path = source_path.replace(CAPTURE_DIR, VAULT_DIR)
    print('Post-processing {}, moving to: {}'.format(source_path, target_path))
    shutil.copyfile(source_path, target_path)
    os.remove(source_path)


def conditionally_create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


if __name__ == '__main__':
    process_face_captures()
