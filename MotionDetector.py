import cv2.cv as cv
import argparse
from datetime import datetime
import time
import cmath
import random
import threading

class MotionDetectorInstantaneous():
    
    def onChange(self, val): #callback when the user change the detection threshold
        self.threshold = val
    
    def __init__(self,threshold=8, videoSrc = None, showWindows=True):
        self.writer = None
        self.font = None
        self.show = showWindows #Either or not show the 2 windows
        self.frame = None

        if videoSrc is None:
            self.capture = cv.CaptureFromCAM(0)
            # otherwise, we are reading from a video file
        else:
            self.capture = cv.CreateFileCapture("rtsp://192.168.128.63:5544/david")

        self.frame = cv.QueryFrame(self.capture) #Take a frame to init recorder

        
        self.frame1gray = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U) #Gray frame at t-1
        cv.CvtColor(self.frame, self.frame1gray, cv.CV_RGB2GRAY)
        
        #Will hold the thresholded result
        self.res = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U)
        # self.redraw = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U)
        self.redraw = cv.CreateImage((self.frame.width, self.frame.height),8,3)

        self.frame2gray = cv.CreateMat(self.frame.height, self.frame.width, cv.CV_8U) #Gray frame at t
        
        self.width = self.frame.width
        self.height = self.frame.height
        self.nb_pixels = self.width * self.height
        self.threshold = threshold
        self.isRecording = False
        self.trigger_time = 0 #Hold timestamp of the last detection
        
        if showWindows:
            cv.NamedWindow("Image")
            cv.CreateTrackbar("Detection treshold: ", "Image", self.threshold, 100, self.onChange)

    def run(self):
        started = time.time()
        while True:
            
            curframe = cv.QueryFrame(self.capture)
            instant = time.time() #Get timestamp o the frame

            self.processImage(curframe) #Process the image

            # if self.somethingHasMoved():
            #     self.trigger_time = instant #Update the trigger_time
            #     if instant > started +5:#Wait 5 second after the webcam start for luminosity adjusting etc..
            #         print datetime.now().strftime("%b %d, %H:%M:%S"), "Something is moving !"
            #     else:
            #         print datetime.now().strftime("%b %d, %H:%M:%S")

            if self.show:
                cv.ShowImage("Image", curframe)
                cv.ShowImage("Res", self.redraw)

            cv.Copy(self.frame2gray, self.frame1gray)
            c=cv.WaitKey(1) % 0x100
            if c==27 or c == 10: #Break if user enters 'Esc'.
                break
    
    def processImage(self, frame):

        # self.redraw = cv.CreateImage((self.frame.width, self.frame.height),8,3)

        cv.CvtColor(frame, self.frame2gray, cv.CV_RGB2GRAY)
        
        # #Absdiff to get the difference between to the frames
        # cv.AbsDiff(self.frame1gray, self.frame2gray, self.res)
        #
        # #Remove the noise and do the threshold
        # cv.Smooth(self.res, self.res, cv.CV_BLUR, 5,5)
        # cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_OPEN)
        # cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_CLOSE)
        # cv.Threshold(self.res, self.res, 10, 255, cv.CV_THRESH_BINARY_INV)

        # print self.redraw.height
        # print self.redraw.width
        # print self.width
        # print self.height

        # self.redraw[50,100] = (255,255,255)

        for x in range(100,self.height,100): #Iterate the hole image
            for y in range(100,self.width,100):
                # print str(x) + '|' + str(y)
                # print frame[x,y]
                height = random.randint(0,self.redraw.height - 101)
                width = random.randint(0,self.redraw.width - 101)
                # print 'random'
                # print str(height) + '|' + str(width)

                for i in range(0,100,1):
                    for j in range(0,100,1):
                        if x+i >= self.height:
                            break
                        if y+j >= self.width:
                            break

                        self.redraw[height + i,width + j] = frame[x + i,y + j]


    def drawTriangle(self, centerPointX, centerPointY, radius):
        point1_x = int(centerPointX - radius * cmath.sqrt(3).real / 2)
        point1_y = int(centerPointY + radius / 2)

        point2_x = int(centerPointX + radius * cmath.sqrt(3).real / 2)
        point2_y = int(centerPointY + radius / 2)

        point3_x = centerPointX
        point3_y = centerPointY - radius

        cv.Line(self.redraw, (point1_x,point1_y), (point2_x,point2_y),(255,255,255),1)
        cv.Line(self.redraw, (point2_x,point2_y), (point3_x,point3_y),(255,255,255),1)
        cv.Line(self.redraw, (point3_x,point3_y), (point1_x,point1_y),(255,255,255),1)

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

    ap = argparse.ArgumentParser()
    ap.add_argument("-v", "--video", help="path to the video file")
    # ap.add_argument("-a", "--min-area", type=int, default=300, help="minimum area size")
    args = vars(ap.parse_args())
    # if the video argument is None, then we are reading from webcam

    detect = MotionDetectorInstantaneous(videoSrc=args.get("video", None))
    detect.run()
