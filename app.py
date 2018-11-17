import os
import time

from base64 import decodebytes
from flask import Flask, redirect, render_template, request, url_for

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
    if encoded_image and label:
        _save_image(encoded_image, label)
        return redirect(url_for('index'))
    return redirect(url_for('index')), 400


def _save_image(encoded_image, label):
    filename = '{}-{}.jpg'.format(label, int(time.time()))
    file_path = os.path.join(app.config['CAPTURE_DIR'], label, filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(decodebytes(encoded_image.encode()))


def _is_allowed_file(filename):
    return any(extension in filename.lower() for extension in ALLOWED_EXTENSIONS)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    HOST = 'localhost'
    app.run(host=HOST, port=PORT, debug=True)
