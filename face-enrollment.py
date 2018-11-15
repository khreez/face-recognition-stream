import os
import cv2
import argparse
import time

from imutils.video import VideoStream
from keras.preprocessing.image import ImageDataGenerator, load_img, img_to_array
from tqdm import tqdm

ENROLLED_DIR = 'enrolled'
AUGMENTED_DIR = 'augmented'

image_width = 160
image_height = 160

datagen = ImageDataGenerator(
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    # brightness_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    fill_mode='nearest',
    horizontal_flip=True)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--identifier", required=True, help="name or class identifier")
args = vars(ap.parse_args())

label = args["identifier"]

label_path = os.path.join(ENROLLED_DIR, label)
if not os.path.exists(label_path):
    os.makedirs(label_path)

target_dir = os.path.join(AUGMENTED_DIR, label)
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

source_sample_count = 0
augmented_sample_count = 0

vs = VideoStream(src=0).start()
time.sleep(2.0)

while True:
    frame = vs.read()
    source = frame.copy()

    cv2.imshow("Frame", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("c"):
        destination_file = os.path.sep.join([ENROLLED_DIR, label, "{}.jpg".format(str(source_sample_count).zfill(5))])
        cv2.imwrite(destination_file, source)
        message = 'Captured face image sample'
        print(message)
        cv2.putText(frame, message, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        source_sample_count += 1

    elif key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()

if source_sample_count > 0:
    print('Took {} sample face image(s) for: {}'.format(source_sample_count, label))

    print('Loading sample face image(s) from: {}'.format(label_path))
    for file_name in tqdm(os.listdir(label_path)):
        image = load_img(os.path.join(label_path, file_name))
        image = img_to_array(image)
        image = image.reshape((1,) + image.shape)
        if image is not None:
            print('Processing image file: {} into: {}'.format(file_name, target_dir))
            for _ in datagen.flow(image, batch_size=1, save_to_dir=target_dir, save_prefix=file_name.split('.')[0],
                                  save_format='jpeg'):
                augmented_sample_count += 1
                if augmented_sample_count > 500:
                    break

    if augmented_sample_count > 0:
        print('Generated {} augmented sample face image(s) for: {}'.format(augmented_sample_count, label))
    else:
        print('No augmented sample face image generated for: {}'.format(label))

else:
    print('No sample face image enrolled for: {}'.format(label))
