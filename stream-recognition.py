import face_recognition
import imutils
import pickle
import cv2
import time

from imutils.video import VideoStream
from sms_alert import send_intruder_alert

ALERT_FREQUENCY = 60 * 1  # alert every x minutes
ALERT_THRESHOLD = 20  # min event count to alert


def capture_stream():
    alert_events = 0  # events counter
    alert_last_check = 0
    data = pickle.loads(open("./encoded_faces.pickle", "rb").read())
    stream = VideoStream(src=0).start()

    while True:
        frame = stream.read()

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb = imutils.resize(rgb, width=750)

        boxes = face_recognition.face_locations(rgb, model='hog')
        encodings = face_recognition.face_encodings(rgb, boxes)

        names = []
        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding, 0.5)

            name = 'Unknown'
            if True in matches:
                matched_idxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}

                for i in matched_idxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                name = max(counts, key=counts.get)

            names.append(name)

        r = frame.shape[1] / float(rgb.shape[1])
        current = time.time()
        time_passed = current - alert_last_check

        for ((top, right, bottom, left), name) in zip(boxes, names):
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)

            if name == 'Unknown':
                colour = (0, 0, 255)

                alert_events += 1
                if alert_events >= ALERT_THRESHOLD:
                    if time_passed >= ALERT_FREQUENCY:
                        send_intruder_alert()
                        cv2.putText(frame, 'alert sent', (left, bottom), cv2.FONT_HERSHEY_SIMPLEX, 0.75, colour, 2)
                        alert_events = 0
                        alert_last_check = current
                    else:
                        alert_events = 0

            else:
                colour = (0, 255, 0)

            cv2.rectangle(frame, (left, top), (right, bottom), colour, 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, colour, 2)

        cv2.imshow('Security stream', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            stream.stop()
            break


if __name__ == '__main__':
    capture_stream()
