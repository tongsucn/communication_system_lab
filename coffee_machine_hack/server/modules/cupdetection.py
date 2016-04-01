##!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging
from threading import Thread
from threading import Lock
import cherrypy
import numpy as np

""" Check if we're able to import opencv. If not, the setup is wrong / incompatible. 
    CupDetection will fallback to Undetermined state. """
hasCV = True
try:
    import cv2
except ImportError as e:
    logging.error('OpenCV could not be loaded. Cup-Detection won\'t be available')
    logging.error(e)
    hasCV = False


class cupDetector():
    frameCount = 0          # Number of processed Frames
    learningRate = -1       # Current learning-rate of the Background-subtractor
    threadActive = False    # If True, the frame-processing-thread is running. Thread will terminate next iteration if set to false.

    deviceId = 0            # Device-id of the camera

    threshArea = 6000      # Threshold area (in pixels) until a detection will be considered a cup
    threshRatio = 0.4       # Threshold for ratio of shape / convex-hull until a detection will be considered a cup

    resX = 1280             # Capture-resolution
    resY = 720

    learningFrames = 50     # number of frames used to initially train the background-detector

    maxContours = 300       # Maximal number of contours processed to prevent too high CPU-load

    dataLock = Lock()       # Mutex for image-matricies

    cap = None              # Will be overwritten with instance of cvCapture

    hasValidFrame = False   # Indicated wether the current Frame has been processed or an error occured

    diffThreshold = 40

    def __init__(self):
        if hasCV:
            self.frame = np.zeros((1, 1, 3), np.uint8)
            self.updateMask = np.zeros((1, 1), np.uint8)
            self.fgmask = np.zeros((1, 1), np.uint8)
            self.currBG = np.zeros((1, 1, 3), np.uint8)
            self.fgbg = cv2.createBackgroundSubtractorMOG2(200, 5, False)

            self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
        else:
            self.frame = None
            self.updateMask = None
            self.fgMaskMOG2 = None
            self.currBG = None

        self.coffeCandidates = []

        logging.info('CupDetection Initialized.')

    # Initializes the configured Camera
    def initializeCamera(self):
        global hasCV
        if not hasCV:
            logging.error('Skipping camera-intialization')
            return

        if self.threadActive:
            logging.error('InitializeCamera called while Thread is still active.')
            return

        # Preconfigure the automatic-controls of the camera using v4l2-utils
        if os.system('v4l2-ctl --silent') == -1:
            logging.error('v4l2-ctl is not available. Install v4l2-utils.')
            return
        if os.system('v4l2-ctl --device={} -c exposure_auto=0'.format(self.deviceId)) == -1:
            logging.error('Could not configure exposure_auto')
            return
        if os.system('v4l2-ctl --device={} -c exposure_absolute=5120'.format(self.deviceId)) == -1:
            logging.error('Could not configure exposure_absolute')
            return

        try:
            self.cap = cv2.VideoCapture(self.deviceId)
        except (cv2.error) as e:
            logging.error('Unable to open camera')
            logging.error(e)
            hasCV = False
            return

        if not self.cap.isOpened():
            logging.error('Could not access camera.')
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resX)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resY)

        # After capture has been opened + resolution has been set, kick of processing thread
        Thread(target=self.threadLoop).start()

    def shutdown(self):
        """ Closes the camera if open + signals the processing thread to shutdown """
        logging.info('Shutting down cupDetection.')
        if self.cap:
            self.cap.release()
        self.threadActive = False

    def encodeImage(self, img):
        """ Encodes the np-array given by img into jpeg-data that can be sent over http """
        if isinstance(img, type(None)) or img.size == 0:
            _, data = cv2.imencode('.jpg', np.zeros((1), np.uint8))
        else:
            with self.dataLock:
                 _, data = cv2.imencode('.jpg', img)
            
        jpeg_data = data.tostring()

        return jpeg_data

    @cherrypy.expose
    def getImage(self, frameId, t):
        """ Returns the given image as http image/jpeg data.
            If the image is not available/invalid, returns a 1x1 black image.
            The t parameter is only used to trick the browser into reloading,
            Has no significance to the python code."""
        del t
        if not hasCV:
            return self.encodeImage(None)
        cherrypy.response.headers['Content-Type'] = "image/jpeg"
        if frameId == 'frame':
            return self.encodeImage(self.frame)
        elif frameId == 'updateMask':
            return self.encodeImage(self.updateMask)
        elif frameId == 'fgmask':
            return self.encodeImage(self.fgmask)
        elif frameId == 'currBG':
            return self.encodeImage(self.currBG)
            
            return self.encodeImage(None)

    @cherrypy.expose
    def hasCup(self):
        """ Returns wether a cup is currently detected.
            Can return 0, 1, or Undetermined.
            If undetermined, the user should be asked to reinitialize the Cup-Detection."""
        if self.hasValidFrame:
            return 'Undetermined'
        if len(self.coffeCandidates) == 0:
            return '0'
        elif len(self.coffeCandidates) <= 4:
            return '1'
        else:
            return 'Undetermined'

    @cherrypy.expose
    def reinitialize(self):
        """ Triggers full recreation of background """
        self.frameCount = 0
        self.learningRate = -1

    def threadLoop(self):
        """ Loop around frameUpdate function. 
            Will exit after currrent Iteration if threadActive is set to false."""
        self.threadActive = True
        while self.threadActive:
            self.frameUpdate()
            time.sleep(1)

    def frameUpdate(self):
        """ Captures + Processes a single Frame """
        if not self.cap.isOpened():
            logging.error('Could not access camera.')
            cv2.waitKey(500)
            return -1

        with self.dataLock:
            ret, self.frame = self.cap.read()

        # If we couldn't capture a frame the camera has been disconnected/some unexpected error occured.
        # Notify the user + exit
        if not ret:
            if self.hasValidFrame:
                logging.warn('Error capturing Frame. Check setup.')
                self.hasValidFrame = False
            cv2.waitKey(500)
            return

        # Apply background-subtraction
        # learningRate will only be != 0 for the first <learningFrames> frames
        # Afterwards, the adaptive masking will take over
        with self.dataLock:
            fgMaskMOG2 = self.fgbg.apply(self.frame, learningRate=self.learningRate)

        self.frameCount += 1

        # Only execute the actual detection after <learningFrames> have passed
        if self.frameCount <= self.learningFrames:
            return

        # Disable automatic learning of BGSub
        self.learningRate = 0

        # Adaptively update the Background-Image
        with self.dataLock:
            self.currBG = self.fgbg.getBackgroundImage()

        # Create an image of pixels with a big enough change (controlled by diffThreshold)
        self.frameDiff = cv2.inRange(cv2.absdiff(self.currBG, self.frame), (self.diffThreshold, self.diffThreshold, self.diffThreshold), (255, 255, 255))

        # Smooth + erode fgmask to remove the minimal noise
        with self.dataLock:
            #self.fgmask = cv2.morphologyEx(self.frameDiff, cv2.MORPH_OPEN, self.kernel)
            self.fgmask = cv2.erode(self.fgmask, self.kernel, iterations=1)
            #self.fgmask = cv2.dilate(self.fgmask, self.kernel, iterations=1)

        # Extract detected contours
        with self.dataLock:
            _, contours, _ = cv2.findContours(self.fgmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        self.coffeCandidates = []
        # Loop over detected Candidates and filter out coffee-candidates
        for cnt in contours:
            cnt = cv2.approxPolyDP(cnt, 5, 1)
            area = cv2.contourArea(cnt)
            hullArea = cv2.contourArea(cv2.convexHull(cnt))
            if area > self.threshArea and float(area) / hullArea > self.threshRatio:
                self.coffeCandidates.append(cv2.convexHull(cnt))

        with self.dataLock:
            self.updateMask = self.fgmask.copy()

        
        # Remove the detected coffe-cup from foreground-mask
        with self.dataLock:
            self.updateMask = self.updateMask & self.frameDiff
            cv2.drawContours(self.updateMask, self.coffeCandidates, -1, (0, 0, 0), -1)
            cv2.drawContours(self.updateMask, self.coffeCandidates, -1, (0, 0, 0), 8)

            # Get everything where the mask is black from the current Background-Model
            img1 = cv2.bitwise_and(self.currBG, self.currBG, mask=(255 - self.updateMask))
            # Get everything where the mask is white from the current Frame
            img2 = cv2.bitwise_and(self.frame, self.frame, mask=self.updateMask)

            # Show contours on current Frame
            cv2.drawContours(self.frame, self.coffeCandidates, -1, (0, 255, 0), 3)
            cv2.drawContours(self.frame, contours, -1, (255, 0, 0), 1)

            # Calculate + update new Background-model
            newBg = img1 | img2
            self.fgbg.apply(newBg, learningRate=-1)

        self.hasValidFrame = True
