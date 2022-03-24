print("[INFO] importing people_counter.py files...")
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse, imutils, dlib, cv2, mysql.connector, time, datetime

#Define classes to objects that will be searched in image
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

print("[INFO] loading model...")
modelFile = "models/MobileNetSSD_deploy.caffemodel"
configFile = "models/MobileNetSSD_deploy.prototxt.txt"
confidence = 0.4
net = cv2.dnn.readNetFromCaffe(configFile, modelFile)

print("[INFO] opening database...")
db = mysql.connector.connect(
     host="localhost",
     user="root",
     passwd="root",
     database="accessController0"
     )

cursor = db.cursor()

print("[INFO] opening video file...")
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--camera", required=True,
	help="IP to analyzed camera")
args = vars(ap.parse_args())
CAMERA = args["camera"]

vs = cv2.VideoCapture(CAMERA)
time.sleep(2.0)

ct = CentroidTracker(maxDisappeared=2)
(H,W) = (None, None)

trackers = []
trackableObjects = {}
totalFrames = 0
cursor.execute("SELECT total FROM Trackers ORDER BY ID DESC LIMIT 1")
totalPeople = list(cursor)[0][0]
skipFrames = 30

fps = FPS().start()

while True:
     try:
          rect, frame = vs.read()
                                    
          frame = imutils.resize(frame,width=500)
          rgb = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
     except:
          break

     if W is None or H is None:
          (H,W) = frame.shape[:2]

     status = "Waiting"
     rects = []

     if totalFrames % skipFrames == 0:
          status = "Detecting"
          trackers = []
               
          blob = cv2.dnn.blobFromImage(frame, 0.007843, (W, H), 127.5)
          net.setInput(blob)
          detections = net.forward()

          for i in range(0, detections.shape[2]):
               conf = detections[0,0,i,2]

               if conf > confidence:
                    idx = int(detections[0,0,i,1])

                    if CLASSES[idx] != "person":
                         continue

                    box = detections[0, 0, i, 3:7] * np.array([W, H, W, H])
                    (startX, startY, endX, endY) = box.astype("int")
                    tracker = dlib.correlation_tracker()
                    rect = dlib.rectangle(int(startX), int(startY), int(endX), int(endY))
                    tracker.start_track(rgb, rect)
                    trackers.append(tracker)
                         
     else:
          for tracker in trackers:
               status = "Tracking"

               tracker.update(rgb)
               pos = tracker.get_position()

               startX = int(pos.left())
               startY = int(pos.top())
               endX = int(pos.right())
               endY = int(pos.bottom())

               rects.append((startX,startY,endX,endY))

     cv2.line(frame,(0,H//2),(W,H//2),(0,255,255),2)
     #cv2.line(frame,(W//2,0),(W//2,H),(0,255,255),2)

     objects = ct.update(rects)

     for (objectID,centroid) in objects.items():
          to = trackableObjects.get(objectID, None)

          if to is None:
               to = TrackableObject(objectID, centroid)

          else:
               y = [c[1] for c in to.centroids]
               direction = centroid[1] - np.mean(y)
               to.centroids.append(centroid)
               
               if not to.counted:                    
                    if direction > 0 and centroid[1] > H // 2:
                         now = datetime.datetime.now()
                         cursor.execute("SELECT total FROM Trackers ORDER BY ID DESC LIMIT 1")
                         totalPeople = list(cursor)[0][0]
                         totalPeople -= 1
                         to.counted = True
                         cursor.execute("INSERT INTO Trackers (direction, total, weekday, datetime) VALUES (%s,%s,%s,%s)",('saindo', totalPeople, now.weekday(),now))
                         db.commit()
                         #print("[INFO] published data on database")
                         
                    elif direction < 0 and centroid[1] < H//2:
                         now = datetime.datetime.now()
                         cursor.execute("SELECT total FROM Trackers ORDER BY ID DESC LIMIT 1")
                         totalPeople = list(cursor)[0][0]
                         totalPeople += 1
                         to.counted = True
                         cursor.execute("INSERT INTO Trackers (direction, total, weekday, datetime) VALUES (%s,%s,%s,%s)",('entrando', totalPeople, now.weekday(),now))
                         db.commit()
                         #print("[INFO] published data on database")
                         

          trackableObjects[objectID] = to
          text = "ID {}".format(objectID)
          cv2.putText(frame, text, (centroid[0] - 10, centroid[1] - 10),
          cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
          cv2.circle(frame, (centroid[0], centroid[1]), 4, (0, 0, 255), -1)

     cv2.putText(frame, "TOTAL: "+str(totalPeople), (10, H),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
##     cv2.putText(frame, "STATUS: "+status, (10, H - 20),
##                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

     cv2.imshow("Frame", frame)
     key = cv2.waitKey(1) & 0xFF

     if key == ord("q"):
          break

               
     totalFrames += 1
     fps.update()
          

fps.stop()
print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))


cv2.destroyAllWindows()
db.close()
