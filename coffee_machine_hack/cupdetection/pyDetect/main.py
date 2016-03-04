import numpy as np
import cv2
import os
import logging


def init():
    global cap, fgbg
    if os.system('v4l2-ctl --silent') == -1:
        logging.error('v4l2-ctl is not available.')
        return -1
    if os.system('v4l2-ctl --device={} -c exposure_auto=0'.format(0)) == -1:
        logging.error('Could not configure exposure_auto')
        return -1
    if os.system('v4l2-ctl --device={} -c exposure_absolute=5120'.format(0)) == -1:
        logging.error('Could not configure exposure_absolute')
        return -1


    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        logging.error('Could not access camera.')
        return -1
    
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,1280);
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,720);

    fgbg = cv2.createBackgroundSubtractorMOG2(500, 16, False)

    #help(fgbg)

    logging.info('Initialization finished.')
    return 0

def shutdown():
    global cap, fgbg
    cap.release()
    cv2.destroyAllWindows()


init()

frameCount = 0
learningRate = -1
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))

while(1):
    ret, frame = cap.read()


    #frame = cv2.GaussianBlur(frame, (7, 7), 0)

    fgMaskMOG2 = fgbg.apply(frame, learningRate=learningRate)

    frameCount += 1
    if frameCount > 100:
        learningRate = 0
        fgmask = cv2.morphologyEx(fgMaskMOG2, cv2.MORPH_OPEN, kernel)

        fgmask = cv2.erode(fgmask,kernel,iterations = 1)
        fgmask = cv2.dilate(fgmask,kernel,iterations = 1)

        im2, contours, hierarchy = cv2.findContours(fgmask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        newContours = []
        filterContours = []
        for cnt in contours:
            cnt = cv2.approxPolyDP(cnt, 5, 1)
            area = cv2.contourArea(cnt)
            hullArea = cv2.contourArea(cv2.convexHull(cnt))
            if area > 500 and float(area) / hullArea > 0.6:
                newContours.append(cv2.convexHull(cnt))
            else:
                if len(filterContours) < 500:
                    filterContours.append(cnt)
                elif len(filterContours) == 500:
                    logging.warn('Too many shapes. Omitting some.')

        currBG = fgbg.getBackgroundImage()

        #help(frame)

        copyMask = np.zeros(fgMaskMOG2.shape, np.uint8)
        cv2.drawContours(copyMask, filterContours, -1, (255,255,255), -1)
        img1 = cv2.bitwise_and(currBG,currBG,mask = 255 -copyMask)
        img2 = cv2.bitwise_and(frame,frame,mask = copyMask)
        #currBG[copyMask] += frame
        #frame.copyTo(currBG, copyMask)
        #currBG.add

        cv2.drawContours(frame, newContours, -1, (0,255,0), 3)

        fgbg.apply(img1 | img2, learningRate = -1)
        cv2.imshow('copymask',copyMask)
        cv2.imshow('mask',fgmask)

    cv2.putText(frame, str(frameCount), (15, 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (0, 0, 0))
    cv2.putText(frame, str(learningRate), (150, 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5 , (0, 0, 0))
    cv2.imshow('frame',frame)
    #cv2.imshow('currBG',currBG)
    #cv2.imshow('newbg',img1 | img2)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

shutdown()