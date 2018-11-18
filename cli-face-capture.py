import os
import cv2
import argparse
import time
import requests
import tempfile

from base64 import b64encode
from imutils.video import VideoStream

API_URL = 'http://localhost:5000/upload'

source_sample_count = 0
message_color = (0, 0, 255)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--identifier", required=True, help="name or class identifier")
args = vars(ap.parse_args())

label = args["identifier"]

vs = VideoStream(src=0).start()
time.sleep(2.0)

while True:
    frame = vs.read()
    source = frame.copy()

    frame_message = 'Face enrollment mode'
    cv2.putText(frame, frame_message, (1, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, message_color, 2)
    cv2.imshow(frame_message, frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("c"):
        destination_file = os.path.join(tempfile.gettempdir(), "{}-{}.jpg".format(label, int(time.time())))
        cv2.imwrite(destination_file, source)

        # TODO need to pass multipart img
        payload = {
            'image': b64encode(open(destination_file, 'rb').read()),
            'label': label
        }
        requests.post(API_URL, data=payload)

        source_sample_count += 1

        capture_message = 'Captured face image sample for: {}'.format(label)
        print(capture_message)
        cv2.putText(frame, capture_message, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, message_color, 2)
        time.sleep(2.0)

    elif key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()

if source_sample_count > 0:
    print('Took {} sample face image(s) for: {}'.format(source_sample_count, label))
else:
    print('No sample face image enrolled for: {}'.format(label))
