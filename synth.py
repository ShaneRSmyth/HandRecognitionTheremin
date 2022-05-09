import cv2
import mediapipe as mp
import math
from tkinter import ttk
import tkinter as tk


class HandDetector:

    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, minTrackCon=0.5):
        
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []
        self.mpStyles = mp.solutions.drawing_styles


    def findHands(self, img, draw=True, flipType=True):
        #convert colour from bgr to rgb
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #detect hands
        self.results = self.hands.process(imgRGB)
        allHands = []
        #3 dimensional shape
        h, w, c = img.shape
        #landmarks detected on the hand
        if self.results.multi_hand_landmarks:
            #landmarks in left or right hand, or both
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {} #dictionary
                ## lmList
                mylmList = []
                xList = []
                yList = []
                #for id of every landmark
                for id, lm in enumerate(handLms.landmark):
                    #x, y and z co ordinates
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)

                ## boundary box
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), \
                         bbox[1] + (bbox[3] // 2)

                #dictionary to create list of landmarks for specified hand
                myHand["lmList"] = mylmList
                #boundary box dictionary
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                #if the hand is flipped around, swap from left to right and right to left
                if flipType:
                    if handType.classification[0].label == "Right":
                        myHand["type"] = "Left"
                    else:
                        myHand["type"] = "Right"
                else:
                    myHand["type"] = handType.classification[0].label
                allHands.append(myHand)

                ## draw pipeline, boundary box, text on screen
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS, self.mpStyles.get_default_hand_landmarks_style(),
                                               self.mpStyles.get_default_hand_connections_style())
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (255, 0, 0), 2)
                    cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                                2, (255, 0, 0), 2)
        if draw:
            return allHands, img
        else:
            return allHands


    def findDistance(self, p1, p2, img = None):
        
        #points of the fingers
        if self.results.multi_hand_landmarks:
            x1, y1 = p1
            x2, y2 = p2
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            self.info = (x1, y1, x2, y2, cx, cy)
        
            #draw circles and line from chosen points.  formula for length of line
            if img is not None:
                cv2.circle(img, (x1, y1), 15, (0, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), 15, (0, 0, 255), cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
                lineLength = math.hypot(x2 - x1, y2 - y1)

                return lineLength, self.info, img
            else:
                return lineLength, self.info



    def fingersUp(self, myHand):

        #type of hand to count fingers
        myHandType = myHand["type"]
        #type of landmarks, left or right hand landmarks
        myLmList = myHand["lmList"]

        if self.results.multi_hand_landmarks:
            fingers = []       
        
            # Thumb
            if myHandType == "Right":
                if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)

                else:
                    fingers.append(0)
            else:
                if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                    
                else:
                    fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            return fingers