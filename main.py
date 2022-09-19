import time
import sys
from turtle import right
import cv2
from cvzone.HandTrackingModule import HandDetector

detector = HandDetector(maxHands=2, detectionCon=0.8)
video = cv2.VideoCapture(0)


# def get_hand_pos(img, hand, h, w):
#     lmList, bbox = detector.findPosition(img, draw=False)
#     print(bbox)


cv2.namedWindow("Resized_Window", cv2.WINDOW_NORMAL)

# Using resizeWindow()
cv2.resizeWindow("Resized_Window", 300, 700)
left_hand, right_hand = 0, 0
left_hand_pos, right_hand_pos = 0, 0

while True:
    _, img = video.read()
    img = cv2.flip(img, 1)
    imS = cv2.resize(img, (960, 540))
    h, w, c = img.shape
    fontScale = (w * h) / (1000 * 1000)
    x, y, h, w = cv2.getWindowImageRect("Resized_Window")
    hands = detector.findHands(img, draw=False)
    if len(hands) == 2:
        hand1 = hands[0]
        lmList1 = hand1["lmList"]
        fingers1 = detector.fingersUp(hand1)
        hand2 = hands[1]
        lmList2 = hand2["lmList"]

        centerPoint1 = hand1['center']
        centerPoint2 = hand2['center']
        img = cv2.putText(img, f"Left hand is at {centerPoint1}",
                          (100, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1)
        img = cv2.putText(img, f"Right hand is at {centerPoint2}", (
            500, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1)

        fingers2 = detector.fingersUp(hand2)
        if hand1['type'] == "Left":
            print("yes")
            right_hand = len([x for x in fingers1 if x == 1])
            left_hand = len([x for x in fingers2 if x == 1])
            #left_hand_pos = get_hand_pos(img, "left", h, w)
            centerPoint1 = hand1['center']
        else:
            left_hand = len([x for x in fingers1 if x == 1])
            right_hand = len([x for x in fingers2 if x == 1])
            #right_hand_pos = get_hand_pos(img, "right", h, w)
        print(left_hand, right_hand)
    cv2.imshow("Resized_Window", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
