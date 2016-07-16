import cv2.cv as cv
import cv2
from datetime import datetime
import time
import numpy as np


class MotionDetectorInstantaneous():

    def onChange(self, val):  # callback when the user change the detection threshold
        self.threshold = val

    def __init__(self, threshold=8, doRecord=False, showWindows=True):
        self.writer = None
        self.font = None
        self.doRecord=doRecord  # Either or not record the moving object
        self.show = showWindows  # Either or not show the 2 windows
        self.frame = None

        self.capture=cv.CaptureFromCAM(0)
        self.frame = cv.QueryFrame(self.capture)  # Take a frame to init recorder
        if doRecord:
            self.initRecorder()

        self.frame1gray = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U)  # Gray frame at t-1
        cv.CvtColor(self.frame, self.frame1gray, cv.CV_RGB2GRAY)

        # Will hold the thresholded result
        self.res = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U)

        self.frame2gray = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U)  # Gray frame at t

        self.width = self.frame.width
        self.height = self.frame.height
        self.nb_pixels = self.width * self.height
        self.threshold = threshold
        self.isRecording = False
        self.trigger_time = 0  # Hold timestamp of the last detection
        self.new = cv.CreateMat(self.height, self.width, cv.CV_8U)

        #  if showWindows:
            #  cv.NamedWindow("Image")
            #  cv.CreateTrackbar("Detection treshold: ", "Image", self.threshold, 100, self.onChange)

    def initRecorder(self):  # Create the recorder
        codec = cv.CV_FOURCC('M', 'J', 'P', 'G')  # ('W', 'M', 'V', '2')
        self.writer=cv.CreateVideoWriter(datetime.now().strftime("%b-%d_%H_%M_%S") +".wmv", codec, 5, cv.GetSize(self.frame), 1)
        # FPS set to 5 because it seems to be the fps of my cam but should be ajusted to your needs
        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 2, 8)  # Creates a font

    def run(self):
        started = time.time()
        while True:

            curframe = cv.QueryFrame(self.capture)
            instant = time.time()  # Get timestamp o the frame

            #  self.processImage(curframe)  # Process the image

            #  if not self.isRecording:
                #  if self.somethingHasMoved():
                    #  self.trigger_time = instant  # Update the trigger_time
                    #  if instant > started +5:  # Wait 5 second after the webcam start for luminosity adjusting etc..
                        #  print datetime.now().strftime("%b %d, %H:%M:%S"), "Something is moving !"
                        #  if self.doRecord:  # set isRecording=True only if we record a video
                            #  self.isRecording = True
            #  else:
                #  if instant >= self.trigger_time +10:  # Record during 10 seconds
                    #  print datetime.now().strftime("%b %d, %H:%M:%S"), "Stop recording"
                    #  self.isRecording = False
                #  else:
                    #  cv.PutText(curframe, datetime.now().strftime("%b %d, %H:%M:%S"), (25, 30), self.font, 0)  # Put date on the frame
                    #  cv.WriteFrame(self.writer, curframe)  # Write the frame
            #  new = cv.CreateMat(720, 1280, cv.CV_8U)
            #  x1 = y1 = 0
            #  for x in range(self.height):
                #  for y in range(self.width):
                    #  if self.res[x, y] != 0.0:
                        #  if (y == y1 or y - y1 < 30) and x - x1 < 90:
                            #  continue
                        #  if (x == x1 or x - x1 < 90)and y - y1 < 30:
                            #  continue
                        #  y1 = y
                        #  x1 = x
                        #  cv.Circle(new, (x, y), 1, (255, 255, 255), -1)
            #  cv.Circle(new, (447, 63), 63, (255, 255, 255), -1)
            #  self.res = new


            #  new = cv.CreateMat(self.height, self.width, cv.CV_8U)
            if self.show:
                #  cv.ShowImage("Image", curframe)
                cv.CvtColor(curframe, self.frame2gray, cv.CV_RGB2GRAY)
                cv.AbsDiff(self.frame1gray, self.frame2gray, self.res)
                cv.Smooth(self.res, self.res, cv.CV_BLUR, 5, 5)
                cv.Threshold(self.res, self.res, 10, 255, cv.CV_THRESH_BINARY_INV)


                #  cv.Copy(self.res, new)
                #  cv.Zero(new)
                cv.Zero(self.new)

                #  vis = np.zeros((self.height, self.width), np.float32)
                #  h,w = vis.shape
                #  vis2 = cv.CreateMat(h, w, cv.CV_32FC3)
                #  vis0 = cv.fromarray(vis)
                #  cv.CvtColor(vis0, vis2, cv.CV_GRAY2RGB)

                #  print vis2
                #  cv.CvtColor(tmp, new, cv.CV_RGB2GRAY)
                #  print self.res
                #  print new
                x1 = y1 = 0
                for x in range(self.height):
                    for y in range(self.width):
                        if self.res[x, y] == 0.0:
                            if (y == y1 or y - y1 < 9) and x - x1 < 11:
                                continue
                            if (x == x1 or x - x1 < 11)and y - y1 < 9:
                                continue
                            y1 = y
                            x1 = x
                            #  cv.Circle(new, (y, x), 2, (255, 255, 255), -1)
                            cv.Circle(self.new, (y, x), 2, (255, 255, 255), -1)
                            #  cv.Circle(vis2, (x, y), 1, (255, 255, 255), -1)
                #  cv.Circle(new, (447, 63), 63, (255, 255, 255), -1)
                #  cv.Circle(vis2, (447, 63), 63, (255, 255, 255), -1)
                #  self.res = new

                #  cv.ShowImage("Res", self.frame2gray)
                #  cv.ShowImage("Res", new)
                cv.ShowImage("Res", self.new)
                #  cv.ShowImage("Res", self.res)
                #  cv.ShowImage("Res", vis2)

            cv.Copy(self.frame2gray, self.frame1gray)
            c=cv.WaitKey(1) % 0x100
            if c==27 or c == 10:  # Break if user enters 'Esc'.
                break

    def processImage(self, frame):
        cv.CvtColor(frame, self.frame2gray, cv.CV_RGB2GRAY)

        #  new = cv.CreateMat(720, 1280, cv.CV_8U)
        #  x1 = y1 = 0
        #  for x in range(self.height):
            #  for y in range(self.width):
                #  if self.res[x, y] != 0.0:
                    #  if (y == y1 or y - y1 < 30) and x - x1 < 90:
                        #  continue
                    #  if (x == x1 or x - x1 < 90)and y - y1 < 30:
                        #  continue
                    #  y1 = y
                    #  x1 = x
                    #  cv.Circle(new, (x, y), 1, (255, 255, 255), -1)
        #  cv.Circle(new, (447, 63), 63, (255, 255, 255), -1)
        #  self.res, new = new, None

        # Absdiff to get the difference between to the frames
        cv.AbsDiff(self.frame1gray, self.frame2gray, self.res)

        # Remove the noise and do the threshold
        cv.Smooth(self.res, self.res, cv.CV_BLUR, 5, 5)
        cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_OPEN)
        cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_CLOSE)
        #  cv.Circle(self.res, (447, 63), 63, (255, 255, 255), -1)
        #  new = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U)


        #  new = cv.CreateMat(720, 1280, cv.CV_8U)
        #  x1 = y1 = 0
        #  t = 30
        #  for x in range(self.height):
            #  for y in range(self.width):
                #  if self.res[x, y] != 0.0:
                    #  if (y == y1 or y - y1 < 30) and x - x1 < 90:
                        #  continue
                    #  if (x == x1 or x - x1 < 90)and y - y1 < 30:
                        #  continue
                    #  y1 = y
                    #  x1 = x
                    #  cv.Circle(new, (x, y), 1, (255, 255, 255), -1)
        #  cv.Circle(new, (447, 63), 63, (255, 255, 255), -1)
        #  self.res, new = new, None

        cv.Threshold(self.res, self.res, 10, 255, cv.CV_THRESH_BINARY_INV)

    def somethingHasMoved(self):
        nb=0  # Will hold the number of black pixels

        for x in range(self.height):  # Iterate the hole image
            for y in range(self.width):
                if self.res[x, y] == 0.0:  # If the pixel is black keep it
                    nb += 1
        avg = (nb *100.0) /self.nb_pixels  # Calculate the average of black pixel in the image

        if avg > self.threshold:  # If over the ceiling trigger the alarm
            return True
        else:
            return False

if __name__=="__main__":
    detect = MotionDetectorInstantaneous(doRecord=False)
    detect.run()
