import os
import time

from base64 import b64decode
from flask import Flask, redirect, render_template, request, url_for
from face_enrollment import generate_facial_augmentation

CAPTURE_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'capture')

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
MAX_IMAGE_SIZE = 6 * 1024 * 1024

app = Flask(__name__)
app.config['ENV'] = 'development'
app.config['CAPTURE_DIR'] = CAPTURE_DIR
app.config['MAX_IMAGE_SIZE'] = MAX_IMAGE_SIZE


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    encoded_image = request.form['image']
    label = request.form['label']
    if _is_allowed_image(encoded_image) and label:
        _process_image(encoded_image, label)
        return redirect(url_for('index'))
    return redirect(url_for('index')), 400


def _process_image(encoded_image, label):
    filename = '{}-{}.jpg'.format(label, int(time.time()))
    image_path = os.path.join(app.config['CAPTURE_DIR'], label, filename)
    print('processing image capture for: {}'.format(label))
    decoded_image = b64decode(encoded_image.encode(), validate=True)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    with open(image_path, "wb") as f:
        f.write(decoded_image)
    print('image stored successfully, requesting facial augmentation for {}'.format(image_path))
    generate_facial_augmentation(image_path, label)


def _is_allowed_image(encoded_image):
    # TODO image verification
    # file_extension = None
    # allowed_extension = any(extension in file_extension for extension in ALLOWED_EXTENSIONS)
    return encoded_image is not None


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    HOST = 'localhost'
    app.run(host=HOST, port=PORT, debug=True)
