import cv2.cv as cv
import argparse
from datetime import datetime
import time
import cmath
import random
import threading

class worker(threading.Thread): #The timer class is derived from the class threading.Thread
    def __init__(self, motionDetector = None, started = None, curframe = None):
        threading.Thread.__init__(self)
        self.motionDetector = motionDetector
        self.started = started
        self.curframe = curframe
        self.thread_stop = False

    def run(self): #Overwrite run() method, put what you want the thread do here
        while not self.thread_stop:
            print self.started

            instant = time.time() #Get timestamp o the frame

            self.motionDetector.processImage(self.curframe) #Process the image

            if not self.isRecording:
                if self.motionDetector.somethingHasMoved():
                    self.trigger_time = instant #Update the trigger_time
                    if instant > self.started +5:#Wait 5 second after the webcam start for luminosity adjusting etc..
                        print datetime.now().strftime("%b %d, %H:%M:%S"), "Something is moving !"
                        if self.motionDetector.doRecord: #set isRecording=True only if we record a video
                            self.isRecording = True
                else:
                    print datetime.now().strftime("%b %d, %H:%M:%S")
            else:
                if instant >= self.trigger_time +10: #Record during 10 seconds
                    print datetime.now().strftime("%b %d, %H:%M:%S"), "Stop recording"
                    self.isRecording = False
                else:
                    cv.PutText(self.curframe,datetime.now().strftime("%b %d, %H:%M:%S"), (25,30),self.motionDetector.font, 0) #Put date on the frame
                    cv.WriteFrame(self.motionDetector.writer, self.curframe) #Write the frame

            if self.motionDetector.show:
                cv.ShowImage("Image", self.curframe)
                cv.ShowImage("Res", self.motionDetector.motionDetector.redraw)

            cv.Copy(self.motionDetector.frame2gray, self.motionDetector.frame1gray)
            self.stop()

    def stop(self):
        print 'thread stop'
        self.thread_stop = True

class MotionDetectorInstantaneous():
    
    def onChange(self, val): #callback when the user change the detection threshold
        self.threshold = val
    
    def __init__(self,threshold=8, videoSrc = None, doRecord=True, showWindows=True):
        self.writer = None
        self.font = None
        self.doRecord=doRecord #Either or not record the moving object
        self.show = showWindows #Either or not show the 2 windows
        self.frame = None

        if videoSrc is None:
            self.capture = cv.CaptureFromCAM(0)
            # otherwise, we are reading from a video file
        else:
            self.capture = cv.CreateFileCapture("rtsp://192.168.128.63:5544/david")

        self.frame = cv.QueryFrame(self.capture) #Take a frame to init recorder
        if doRecord:
            self.initRecorder()
        
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
        
    def initRecorder(self): #Create the recorder
        codec = cv.CV_FOURCC('M', 'J', 'P', 'G') #('W', 'M', 'V', '2')
        self.writer=cv.CreateVideoWriter(datetime.now().strftime("%b-%d_%H_%M_%S")+".wmv", codec, 5, cv.GetSize(self.frame), 1)
        #FPS set to 5 because it seems to be the fps of my cam but should be ajusted to your needs
        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_SIMPLEX, 1, 1, 0, 2, 8) #Creates a font

    def run(self):
        started = time.time()
        while True:
            curframe = cv.QueryFrame(self.capture)
            thread = worker(motionDetector = self, started = started, curframe = curframe)
            thread.start()

    
    def processImage(self, frame):

        # self.redraw = cv.CreateImage((self.frame.width, self.frame.height),8,3)

        cv.CvtColor(frame, self.frame2gray, cv.CV_RGB2GRAY)
        
        #Absdiff to get the difference between to the frames
        cv.AbsDiff(self.frame1gray, self.frame2gray, self.res)
        
        #Remove the noise and do the threshold
        cv.Smooth(self.res, self.res, cv.CV_BLUR, 5,5)
        cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_OPEN)
        cv.MorphologyEx(self.res, self.res, None, None, cv.CV_MOP_CLOSE)
        cv.Threshold(self.res, self.res, 10, 255, cv.CV_THRESH_BINARY_INV)

        # print self.redraw.height
        # print self.redraw.width
        # print self.width
        # print self.height

        for x in range(self.height): #Iterate the hole image
            for y in range(self.width):
                if frame[x,y] != 0.0: #If the pixel is black keep it
                    # print str(x) + '|' + str(y)
                    # print frame[x,y]
                    height = random.randint(1,self.redraw.height - 1)
                    width = random.randint(1,self.redraw.width - 1)
                    # print 'random'
                    # print str(height) + '|' + str(width)

                    self.redraw[height,width] = frame[x,y]


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

    detect = MotionDetectorInstantaneous(doRecord=False,videoSrc=args.get("video", None))
    detect.run()
