__author__ = 'sergiochan'

from pyimagesearch.tempimage import TempImage
from picamera.array import PiRGBArray
from picamera import PiCamera
from datetime import datetime
import time
import cv2.cv as cv
import cv2

class MotionDetector():

    def __init__(self,threshold=8):
        self.frame = None

        self.height = 480
        self.width = 640

        self.camera = PiCamera()
        self.camera.resolution = (self.width, self.height)
        self.camera.framerate = 16
        self.rawCapture = PiRGBArray(self.camera, size=(self.width, self.height))

        self.frame1gray = None
            # cv.CreateMat(self.height, self.width, cv.CV_8U) #Gray frame at t-1
        # cv.CvtColor(self.frame, self.frame1gray, cv.CV_RGB2GRAY)

        #Will hold the thresholded result
        self.res = cv.CreateMat(self.height, self.width, cv.CV_8U)

        self.frame2gray = None # cv.CreateMat(self.height, self.width, cv.CV_8U) #Gray frame at t

        self.nb_pixels = self.width * self.height
        self.threshold = threshold
        self.isFirst = True

        cv.NamedWindow("Image")

    def run(self):
        started = time.time()
        for f in self.camera.capture_continuous(self.rawCapture, format="bgr", use_video_port=True):
            curframe = f.array
            instant = time.time() #Get timestamp o the fram

            if self.isFirst:
                self.frame1gray = cv2.cvtColor(curframe, cv2.COLOR_BGR2GRAY)
                self.isFirst = False
            else:
                self.processImage(curframe) #Process the image

                if self.somethingHasMoved():
                    self.trigger_time = instant #Update the trigger_time
                    if instant > started +5:#Wait 5 second after the webcam start for luminosity adjusting etc..
                        print datetime.now().strftime("%b %d, %H:%M:%S"), "Something is moving !"
                else:
                    print datetime.now().strftime("%b %d, %H:%M:%S")

                cv.ShowImage("Image", curframe)
                cv.ShowImage("Res", self.res)

                cv.Copy(self.frame2gray, self.frame1gray)
                c=cv.WaitKey(1) % 0x100
                if c==27 or c == 10: #Break if user enters 'Esc'.
                    break

    def processImage(self, frame):
        self.frame2gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #Absdiff to get the difference between to the frames
        cv.AbsDiff(self.frame1gray, self.frame2gray, self.res)

        #Remove the noise and do the threshold
        cv.Smooth(self.res, self.res, cv.CV_BLUR, 5,5)
        cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_OPEN)
        cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_CLOSE)
        cv.Threshold(self.res, self.res, 10, 255, cv.CV_THRESH_BINARY_INV)

    def somethingHasMoved(self):
        nb=0 #Will hold the number of black pixels

        for x in range(self.height): #Iterate the hole image
            for y in range(self.width):
                if self.res[x,y] == 0.0: #If the pixel is black keep it
                    nb += 1
        avg = (nb*100.0)/self.nb_pixels #Calculate the average of black pixel in the image

        if avg > self.threshold:#If over the ceiling trigger the alarm
            return True
        else:
            return False

if __name__=="__main__":
    detect = MotionDetector()
    detect.run()

