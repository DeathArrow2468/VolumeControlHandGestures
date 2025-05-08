import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#FIX the RATE at which VOLUME is Changing

#########################
wCam, hCam  = 640, 480
#########################
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
pTime = 0

#From pycaw#
#detector = htm.handDetector(detectionCon=0.7, maxHands=1)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()  #-96.0, 0.0  for us
#volume.SetMasterVolumeLevel(-75.0, None)    #Yes, this literally controls the volume
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
#######
volPer=0
area = 0

detector = htm.handDetector(detectionCon=0.7, maxHands=1)
colorVolume = (255, 0, 0)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img, draw=True)
    if len(lmlist) != 0:

        # Filter based on size
        area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) // 100
        #print(area)
        if 120<area<800:
            #Find the distance between index and thumb
            length, img, lineInfo = detector.findDistance(4, 8, img)

            # Convert volume
            
            volBar = np.interp(length, [50, 215], [400, 150])
            volPer = np.interp(length, [50, 215], [0, 100])

            # Reduce Resolution(That is the skips the volume can take, like how Windows vol always goes up/down only by 2) to make it smoother
            smoothness = 2  #Decides by how much can volume increment by
            volPer = smoothness * round(volPer/smoothness)
            
            # Check fingers which are up
            fingers = detector.fingersUp()
            #print(fingers)
            
            # if pinky is down set volume
            if not fingers[4]:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, colorVol, cv2.FILLED)
                volume.SetMasterVolumeLevelScalar(volPer/100, None)
                colorVol = (255, 255, 255)
                time.sleep(0.25)
            else:
                colorVol = (255, 0, 0)
            #print(lmlist[4], lmlist[8])
            
            #print(length)

            # Hand range is 50 to 215
            # Vol. range is -96.0 to 0
            if length<=50:
                cv2.circle(img, (lineInfo[4], lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)


        # Drawings
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3 )
        currentVol = int(volume.GetMasterVolumeLevelScalar()*100)
        cv2.putText(img, f"Vol. Set: {currentVol}", (400,50), cv2.FONT_HERSHEY_COMPLEX, 1, colorVol, 3) 


    # Frame rate
    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"{int(fps)}", (40,70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3) 

    cv2.imshow("Img", img)
    cv2.waitKey(1)