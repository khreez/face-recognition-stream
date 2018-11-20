import os
import time
import utils

from flask import Flask, redirect, render_template, request, jsonify
from face_enrollment import enroll_faces

CAPTURE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), utils.CAPTURE_DIR)

ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg'}
MAX_IMAGE_SIZE = 6 * 1024 * 1024

app = Flask(__name__)
app.secret_key = 'ssucMko8+slOAX3F'
app.config['CAPTURE_PATH'] = CAPTURE_PATH
app.config['MAX_IMAGE_SIZE'] = MAX_IMAGE_SIZE


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/capture', methods=['POST'])
def upload():
    if 'image' in request.files:
        image = request.files['image']
        label = request.form['label']
        if _is_allowed_filename(image.filename) and label:
            filename = _process_image(image, label)
            return jsonify({'filename': filename})
        return redirect(request.url, 400)


@app.route('/enroll', methods=['GET'])
def enroll():
    print('requesting facial enrollment')
    enroll_faces()
    return jsonify({'message': 'completed facial enrollment'})


def _process_image(image, label):
    print('processing image capture for: {}'.format(label))
    filename = '{}-{}.jpg'.format(label, str(time.time()).replace('.', ''))
    image_path = os.path.join(app.config['CAPTURE_PATH'], label, filename)
    os.makedirs(os.path.dirname(image_path), exist_ok=True)
    image.save(image_path)
    print('image stored successfully: {}'.format(image_path))
    return filename


def _is_allowed_filename(filename):
    return any(extension in filename.lower() for extension in ALLOWED_EXTENSIONS)


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    HOST = 'localhost'
    app.run(host=HOST, port=PORT, debug=True)
