
import cv2
from cvzone.HandTrackingModule import HandDetector

detector = HandDetector(maxHands=2, detectionCon=0.8)
video = cv2.VideoCapture(0)
left_hand, right_hand = 0, 0
while True:
    _, img = video.read()
    img = cv2.flip(img, 1)
    hands = detector.findHands(img, draw=False)
    if len(hands) == 2:
        hand1 = hands[0]
        lmList1 = hand1["lmList"]
        fingers1 = detector.fingersUp(hand1)
        hand2 = hands[1]
        lmList2 = hand2["lmList"]
        fingers2 = detector.fingersUp(hand2)
        if hand1['type'] == "Left":
            left_hand = len([x for x in fingers1 if x == 1])
            right_hand = len([x for x in fingers2 if x == 1])
        else:
            right_hand = len([x for x in fingers1 if x == 1])
            left_hand = len([x for x in fingers2 if x == 1])
        print(left_hand, right_hand)
    cv2.imshow("Video", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
