#include <cv.h>
#include <highgui.h>
#include <stdio.h>

int main(int argc, char *argv[])
{
    CvCapture* cap = cvCaptureFromCAM(0);
    IplImage* frame = cvQueryFrame(cap);
    int height = frame->height;
    int width = frame->width;
    int height_new = height;
    int width_new = width;
#ifdef __PI
    height_new = 720;
    width_new = 1280;
#endif
    CvMat* frame1gray = cvCreateMat(frame->height, frame->width, CV_8U);
    CvMat* frame2gray = cvCreateMat(frame->height, frame->width, CV_8U);
    CvMat* res = cvCreateMat(frame->height, frame->width, CV_8U);
    /* CvMat* new = cvCreateMat(height, width, CV_8U); */  // 单通道灰度图
    CvMat* new = cvCreateMat(height, width, CV_8UC3);  // 3通道RGB
#ifdef __PI
    CvMat* resized = cvCreateMat(height_new, width_new, CV_8UC3);
    cvNamedWindow("Res", CV_WINDOW_NORMAL);
    cvSetWindowProperty("Res", CV_WND_PROP_FULLSCREEN, CV_WINDOW_FULLSCREEN);
#endif
    int x = 0;
    int y = 0;
    int x1 = 0;
    int y1 = 0;
    int n_points = 0;
    int R = 10;
    int step = 2 * R;
    unsigned char tmp = 0;
    CvScalar white = CV_RGB(255, 255, 255);
    CvScalar ty_blue = CV_RGB(102,204,255);
    for (;;) {
        frame = cvQueryFrame(cap);
        cvCvtColor(frame, frame2gray, CV_RGB2GRAY);
        cvAbsDiff(frame1gray, frame2gray, res);
        cvSmooth(res, res, CV_BLUR, 5, 5, 0, 0);
        cvThreshold(res, res, 10, 255, CV_THRESH_BINARY_INV);
        /* cvSet(new, CV_RGB(255, 255, 255), NULL); */
        cvSet(new, white, NULL);

        for( x = R; x < height - R; x += step) {
            for (y = R; y < width - R; y += step) {
                n_points = 0;
                for (x1 = x - R; x1 < x+R; x1++) {
                    for (y1 = y - R; y1 < y + R; y1++) {
                        tmp = CV_MAT_ELEM(*res, unsigned char, x1, y1);
                        if (tmp == 0){
                            n_points ++;
                        }
                    }
                }

                if (((n_points * 100) / (2 * R * 2 * R)) > 30) {
                    CvPoint Points[3] = {
#ifdef  __PI
                        {(y - 0.866f * R), (x - 0.5f * R)},
                        {(y + 0.866f * R), (x - 0.5f * R)},
                        {y, (x + R)}
#else
                        {(y - 0.866f * R), (x + 0.5f * R)},
                        {(y + 0.866f * R), (x + 0.5f * R)},
                        {y, (x - R)}
#endif
                    };
                    /* cvFillConvexPoly(new, Points, 3, CV_RGB(102,204,255), 8, 0); */
                    cvFillConvexPoly(new, Points, 3, ty_blue, 8, 0);
                    /* cvCircle(new, cvPoint(y, x), R, CV_RGB(100, 200, 100), -1, 8, 0); */
                    /* cvCircle(new, cvPoint(y, x), R, CV_RGB(100, 200, 100), 0, 8, 0); */
                }

            }
        }

#ifdef __PI
    cvResize(new, resized, CV_INTER_LINEAR);
    cvFlip(resized, resized, 0);
    cvShowImage("Res", resized);
#else
    cvFlip(new, new, 1);
    cvShowImage("Res", new);
#endif
        cvCopy(frame2gray, frame1gray, NULL);
        if(cvWaitKey(30) >= 0) break;
    }
    cvReleaseCapture(&cap);
    cvDestroyAllWindows();
    return 0;
}
