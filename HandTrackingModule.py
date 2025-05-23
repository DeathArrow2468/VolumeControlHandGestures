import cv2
import mediapipe as mp
import time
import math

#print(mp.__version__)

class handDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        #print("Initializing handDetector...")
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        try:
            #print("Creating MediaPipe Hands object...")
            self.mpHands = mp.solutions.hands

            assert isinstance(self.detectionCon, (int, float)), "detectionCon must be int or float"
            assert isinstance(self.trackCon, (int, float)), "trackCon must be int or float"
            assert 0 <= self.detectionCon <= 1, "detectionCon must be between 0 and 1"
            assert 0 <= self.trackCon <= 1, "trackCon must be between 0 and 1"


            self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                            min_detection_confidence=float(self.detectionCon),
                                            min_tracking_confidence=float(self.trackCon))
           # print("MediaPipe Hands object created successfully.")
        except Exception as e:
            print(f"Error during MediaPipe Hands initialization: {e}")

        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        #print("handDetector initialization completed.")


    def findHands(self, img, draw=True):
        #print("findHands called...")
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #print("Image converted to RGB...")
        self.results = self.hands.process(imgRGB)
        #print(f"Results: {self.results}")
        # print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    #print("Drawing landmarks...")
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        #print("findPosition called...")
        xList = []
        yList = []
        bbox = []
        self.lmList = []

        if self.results and self.results.multi_hand_landmarks:

            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                xList.append(cx)
                yList.append(cy)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            xmin, xmax = min(xList), max(xList)
            ymin, ymax = min(yList), max(yList)
            bbox = xmin, ymin, xmax, ymax

            if draw:
                cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                            (bbox[2] + 20, bbox[3] + 20), (255, 0, 225), 2)
                
        return self.lmList, bbox

    def fingersUp(self):
        fingers = []
        #Thumb
        if self.lmList[self.tipIds[0]][1] > self.lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        # 4 Fingers
        for id in range(1, 5):
            if self.lmList[self.tipIds[id]][2] < self.lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, draw=True):
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]

def main():
    #print("Starting main function...")
    pTime = 0
    cap = cv2.VideoCapture(0)
    #print("VideoCapture initialized...")
    
    #print("Initializing handDetector...")
    detector = handDetector()
    #print("Detector initialized successfully!")
    
    while True:
        #print("Inside the loop...")
        success, img = cap.read()
        if not success:
            print("Failed to capture image from webcam.")
            break
        #print("Image captured successfully.")
        
        # Skipping detector methods
        #print("Calling findHands...")
        img = detector.findHands(img)
        lmList, bbox = detector.findPosition(img)
        
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow("Image", img)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            #print("Exiting loop...")
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Program terminated.")


if __name__ == "__main__":
    main()
