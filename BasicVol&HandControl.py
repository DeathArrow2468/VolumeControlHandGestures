import cv2
import time
import numpy as np
import HandTrackingModule as htm
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

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

detector = htm.handDetector(detectionCon=0.7)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmlist, bbox = detector.findPosition(img, draw=False)
    if len(lmlist) != 0:
        #print(lmlist[4], lmlist[8])

        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = (x1+x2)//2, (y1+y2)//2

        cv2.circle(img, (x1, y1), 15, (225, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (225, 0, 0), cv2.FILLED)
        cv2.circle(img, (cx, cy), 15, (225, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (25, 30, 255), 3)

        length = math.hypot(x2-x1, y2-y1)
        #print(length)

        # Hand range is 50 to 215
        # Vol. range is -96.0 to 0
        vol = np.interp(length, [50, 215], [minVol, maxVol])
        volBar = np.interp(length, [50, 215], [400, 150])
        volPer = np.interp(length, [50, 215], [0, 100])
        print(vol)
        volume.SetMasterVolumeLevel(vol, None)

        if length <= 50:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)
        cv2.rectangle(img, (50, 150), (85, 400), (0, 255, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3 )

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime

    cv2.putText(img, f"{int(fps)}", (40,70), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 3) 

    cv2.imshow("Img", img)
    cv2.waitKey(1)