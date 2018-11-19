import os
import time

from flask import Flask, redirect, render_template, request, url_for
from face_enrollment import enroll_face

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
    image = request.files['image']
    label = request.form['label']
    if _is_allowed_filename(image.filename) and label:
        _process_image(image, label)
        return redirect(url_for('index'))
    return redirect(request.url), 400


def _process_image(image, label):
    filename = '{}-{}.jpg'.format(label, int(time.time()))
    image_path = os.path.join(app.config['CAPTURE_DIR'], label, filename)
    print('processing image capture for: {}'.format(label))
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    image.save(image_path)
    print('image stored successfully, requesting facial augmentation for {}'.format(image_path))
    enroll_face(image_path, label)


def _is_allowed_filename(filename):
    return any(extension in filename.lower() for extension in ALLOWED_EXTENSIONS)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    HOST = 'localhost'
    app.run(host=HOST, port=PORT, debug=True)
