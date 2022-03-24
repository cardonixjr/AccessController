import os, time
from threading import Thread

class CameraTh(Thread):
     '''
     Class used to execute the "people_counter.py" code, that capture the image
     from the camera (or video), detect people in this image, track they and
     publish in database if the person enter our leave the establishment.
     '''
     def __init__(self,camera):
          '''Builds the camera Thread'''
          Thread.__init__(self)
          self.camera = camera

     def run(self):
          '''Runs the camera Thread'''
          os.system('py people_counter.py --camera '+camera)

class AppTh(Thread):
     '''
     Class used to execute the "app.py" code, that read the database and
     publishes the information on a webpage in localhost:5000
     '''
     def __init__(self):
          '''Builds the application Thread'''
          Thread.__init__(self)

     def run(self):
          '''Runs the application Thread'''
          os.system('py app.py')

#Start the Application thread
thread = AppTh()
thread.start()

time.sleep(1)

#Define the IP used to connect with the cameras
#You need to edit it and put a RTSP ID
cameras = ['"rtsp://##############"',
           '"rtsp://##############"']

#Run one camera Thread for each camera
for camera in cameras:
     thread = CameraTh(camera)
     thread.start()

