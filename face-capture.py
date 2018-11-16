import os
import cv2
import argparse
import time

from imutils.video import VideoStream

ENROLLED_DIR = 'enrolled'

source_sample_count = 0
augmented_sample_count = 0
message_color = (0, 0, 255)

ap = argparse.ArgumentParser()
ap.add_argument("-i", "--identifier", required=True, help="name or class identifier")
args = vars(ap.parse_args())

label = args["identifier"]

label_path = os.path.join(ENROLLED_DIR, label)
if not os.path.exists(label_path):
    os.makedirs(label_path)

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
        destination_file = os.path.sep.join([ENROLLED_DIR, label, "{}.jpg".format(str(source_sample_count).zfill(5))])
        cv2.imwrite(destination_file, source)
        source_sample_count += 1

        capture_message = 'Captured face image sample'
        print(capture_message)
        # cv2.putText(frame, message, (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, message_color, 2)
        time.sleep(2.0)

    elif key == ord("q"):
        break

cv2.destroyAllWindows()
vs.stop()

if source_sample_count > 0:
    print('Took {} sample face image(s) for: {}'.format(source_sample_count, label))
else:
    print('No sample face image enrolled for: {}'.format(label))
