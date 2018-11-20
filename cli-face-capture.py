import os
import cv2
import argparse
import time
import requests
import tempfile

from imutils.video import VideoStream

API_URL = 'http://localhost:5000/upload'
MESSAGE_COLOR = (0, 0, 255)


def capture_stream(label):
    source_sample_count = 0
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

    while True:
        frame = vs.read()
        source = frame.copy()

        frame_message = 'Face enrollment mode'
        cv2.putText(frame, frame_message, (1, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.75, MESSAGE_COLOR, 2)
        cv2.imshow(frame_message, frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('c'):
            destination_file = os.path.join(tempfile.gettempdir(), '{}-{}.jpg'.format(label, int(time.time())))
            cv2.imwrite(destination_file, source)

            try:
                response = requests.post(API_URL, files={'image': open(destination_file, 'rb')}, data={'label': label})

                if response and response.ok:
                    source_sample_count += 1
                    capture_message = 'Captured face image sample for: {}'.format(label)
                    print(capture_message)
                    cv2.putText(frame, capture_message, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, MESSAGE_COLOR, 2)
                    time.sleep(2.0)
                else:
                    print('unable to submit face capture')

            except requests.RequestException:
                print('unreachable endpoint')

        elif key == ord('q'):
            cv2.destroyAllWindows()
            vs.stop()
            break

    if source_sample_count > 0:
        print('Took {} sample face image(s) for: {}'.format(source_sample_count, label))
    else:
        print('No sample face image enrolled for: {}'.format(label))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('-l', '--label', required=True, help='name or label for the image')
    args = vars(ap.parse_args())

    capture_stream(args['label'])
