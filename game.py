import random
import time
import sys
from turtle import right
import cv2
from cvzone.HandTrackingModule import HandDetector

detector = HandDetector(maxHands=2, detectionCon=0.8)


class LeftHand:
    def __init__(self, fingerCount, in_play=True):
        self.fingerCount = fingerCount
        self.in_play = in_play
        self.name = "left"

    def __add__(self, value):
        self.fingerCount += value
        return self

    def __sub__(self, value):
        self.fingerCount -= value
        return self

    def __eq__(self, value):
        self.fingerCount = value


class RightHand:
    def __init__(self, fingerCount, in_play=True):
        self.fingerCount = fingerCount
        self.in_play = in_play
        self.name = "right"

    def __add__(self, value):
        self.fingerCount += value
        return self

    def __sub__(self, value):
        self.fingerCount -= value
        return self

    def __eq__(self, value):
        self.fingerCount = value


class Combination:
    def __init__(self, hand1, hand2):
        self.hand1 = hand1
        self.hand2 = hand2

    def __iter__(self):
        return self

    def countFingers(self, hand1, hand2):
        return (hand1.fingerCount, hand2.fingerCount)


class Engine:
    def __init__(self):
        self.humanRightHand = RightHand(1)
        self.humanLeftHand = LeftHand(1)
        self.engineRightHand = RightHand(1)
        self.engineLeftHand = LeftHand(1)
        self.engineLeftHand.fingerCount = 1
        self.combinations = [Combination(self.engineRightHand, self.humanRightHand),
                             Combination(self.engineLeftHand,
                                         self.humanLeftHand),
                             Combination(self.engineRightHand,
                                         self.humanLeftHand),
                             Combination(self.engineLeftHand, self.humanRightHand)]

        self.lastEngineMove = ''
        self.prevUserMove = ''

    def display_stats(self):
        print("EngineLeftHand: ", self.engineLeftHand.fingerCount,
              "\tEngineRightHand: ", self.engineRightHand.fingerCount)

        print("HumanLeftHand: ", self.humanLeftHand.fingerCount,
              "\thumanRightHand: ", self.humanRightHand.fingerCount)
        print()

    def start_game(self):
        def performMove(engineHand, humanHand):
            print("Engine attacked on : ", humanHand.name,
                  "with ", engineHand.name)
            humanHand.fingerCount = (
                humanHand.fingerCount + engineHand.fingerCount) % 5
            if humanHand.fingerCount == 5 or humanHand.fingerCount == 0:
                humanHand.in_play = False
                humanHand.fingerCount = 0
                print("human's", humanHand.name,
                      "hand is now out of play!")
                otherHand = self.humanRightHand if humanHand.name == "left" else self.humanLeftHand
                if not otherHand.in_play:
                    self.display_stats()
                    return True
                return
            optimals = []
            for combination in self.combinations:
                engineHand, humanHand = combination.hand1, combination.hand2
                if not humanHand.in_play or not engineHand.in_play:
                    continue
                optimal = self.validate(engineHand, humanHand)
                if optimal == "OK":  # One possible solution found
                    optimals.append((engineHand, humanHand))
                    continue
                if optimal is True:  # Most optimal found!
                    if performMove(engineHand, humanHand):
                        return True
                    return
            if not optimals:  # No optimal solutions found!
                return False

            engineHand, humanHand = random.choice(optimals)
            # Well, computer decides to make a random move, might get lucky if user does not make the right move!
            if performMove(engineHand, humanHand):
                return True
        detector = HandDetector(maxHands=2, detectionCon=0.8)

        cv2.namedWindow("Chopsticks game - AI", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Chopsticks game - AI",
                              cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.resizeWindow("Chopsticks game - AI", 1280, 700)

        left_hand, right_hand = 0, 0
        c = 0
        video = cv2.VideoCapture(0)
        video.set(0, 700)
        video.set(1, 1280)
        stealthMode = False
        user_move = ''
        attacked = False
        while True:
            # self.display_stats()
            if self.engineLeftHand.fingerCount == 0 and self.engineRightHand.fingerCount == 0:
                sys.exit("User won!")
            _, img = video.read()
            img = cv2.flip(img, 1)
            imS = cv2.resize(img, (960, 540))
            h, w, c = img.shape
            fontScale = (w * h) / (1000 * 1000)
            # print(fontScale, '1')
            x, y, h, w = cv2.getWindowImageRect("Chopsticks game - AI")
            hands = detector.findHands(img, draw=False)

            img = cv2.putText(img, f"Computer Left hand count:  {self.engineLeftHand.fingerCount}",
                              (50, 50), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
            img = cv2.putText(img, f"Computer Right hand count:  {self.engineRightHand.fingerCount}", (
                300, 50), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)

            cv2.putText(img, self.lastEngineMove, (
                300, 250), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
            cv2.putText(img, self.prevUserMove, (
                300, 190), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)

            img = cv2.putText(img, f"Actual Left hand count:  {self.humanLeftHand.fingerCount}",
                              (50, 300), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
            img = cv2.putText(img, f"Actual Right hand count:  {self.humanRightHand.fingerCount}", (
                450, 300), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)

            if len(hands) == 2:
                hand1 = hands[0]
                lmList1 = hand1["lmList"]
                fingers1 = detector.fingersUp(hand1)
                hand2 = hands[1]
                lmList2 = hand2["lmList"]

                centerPoint1 = hand2['center'] if hand1['type'] == 'Left' else hand1['center']
                centerPoint2 = hand1['center'] if hand2['type'] == 'Right' else hand2['center']
                fingers2 = detector.fingersUp(hand2)
                # print(hand1, hand2)
                attacked = False
                if hand1['type'] == "Left":
                    right_hand = len([x for x in fingers1 if x == 1])
                    left_hand = len([x for x in fingers2 if x == 1])
                    # left_hand_pos = get_hand_pos(img, "left", h, w)
                else:
                    left_hand = len([x for x in fingers1 if x == 1])
                    right_hand = len([x for x in fingers2 if x == 1])
                    # right_hand_pos = get_hand_pos(img, "right", h, w)
                # print(left_hand, right_hand)

                img = cv2.putText(img, f"Left hand is at {centerPoint1}",
                                  (100, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                img = cv2.putText(img, f"Right hand is at {centerPoint2}", (
                    500, 200), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)

                img = cv2.putText(img, f"Detected Left hand count:  {left_hand}",
                                  (50, 450), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                img = cv2.putText(img, f"Detected Right hand count:  {right_hand}", (
                    450, 450), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                if left_hand or right_hand:
                    print(centerPoint1)
                    if centerPoint1[0] > 300:
                        print("Left hand attacked on engine right")
                        self.prevUserMove = "Left hand attacked on engine right"
                        print(centerPoint1)
                        # sys.exit()
                        attacked = True
                        user_move = "AR-L"
                        img = cv2.putText(img, f"Left hand attacked on engine right", (
                            300, 250), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                        engineHand = self.engineRightHand
                        userHand = self.humanLeftHand
                        time.sleep(0.4)
                    elif centerPoint2[0] < 350:
                        attacked = True

                        print("Right hand attacked on engine left")
                        self.prevUserMove = "Right hand attacked on engine left"
                        print(centerPoint2)
                        # sys.exit()

                        stealthMode = True
                        user_move = "AL-R"
                        img = cv2.putText(img, f"Right hand attacked on engine left", (
                            300, 250), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                        print(centerPoint2)
                        stealthMode = False
                        engineHand = self.engineLeftHand
                        userHand = self.humanRightHand
                        time.sleep(0.4)
                    elif centerPoint1[1] < 250:
                        print("Left hand attacked engine left")
                        self.prevUserMove = "Left hand attacked engine left"
                        print(centerPoint1)
                        # sys.exit()
                        attacked = True
                        user_move = "AL-L"
                        img = cv2.putText(img, f"Left hand attacked engine left", (
                            300, 250), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                        engineHand = self.engineLeftHand
                        userHand = self.humanLeftHand
                        time.sleep(0.4)
                    elif centerPoint2[1] < 260:
                        print(centerPoint2)
                        # sys.exit()

                        user_move = "AR-R"
                        print("Right hand attacked on engine right")
                        self.prevUserMove = "Right hand attacked on engine right"
                        attacked = True
                        img = cv2.putText(img, f"Right hand attacked on engine right", (
                            300, 250), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                        engineHand = self.engineRightHand
                        userHand = self.humanRightHand
                        time.sleep(0.4)
            else:
                if attacked and user_move:
                    print(user_move)
                    attacked = False

                    print(left_hand, right_hand)
                    # Allow time for user to withdraw their hand after attack
                    if user_move.startswith("AL"):
                        if not self.engineLeftHand.in_play:
                            print("EngineLeftHand is not in play!")
                            continue
                        elif not userHand.in_play:
                            print("You are not allowed to use that hand!")
                            continue
                        print("yes incrementing",
                              self.engineLeftHand.fingerCount)
                        self.engineLeftHand.fingerCount = (
                            self.engineLeftHand.fingerCount + userHand.fingerCount) % 5
                        if self.engineLeftHand.fingerCount == 5:
                            self.engineLeftHand.in_play = False
                            self.engineLeftHand.fingerCount = 0
                            print("Engine's left hand is now out of play!")
                            if self.engineRightHand.in_play is False:
                                print("User won!")
                                self.display_stats()
                                sys.exit()
                                return False
                    if user_move.startswith("AR"):
                        if not self.engineRightHand.in_play:
                            print("engineRightHand is not in play!")
                            continue
                        self.engineRightHand.fingerCount = (
                            self.engineRightHand.fingerCount + userHand.fingerCount) % 5
                        if (self.engineRightHand).fingerCount == 5:
                            self.engineRightHand.in_play = False
                            self.engineRightHand.fingerCount = 0
                            print("Engine's right hand is now out of play!")
                            if self.engineLeftHand.in_play is False:
                                print("User won!")
                                sys.exit()
                                return False
                    res = self.runOptimalMove(img, w, h)
                    if res:
                        print("Computer won!")
                        img = cv2.putText(img, f"COMPUTER WON!! :(", (
                            10, 10), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (0, 0, 255), 1, lineType=cv2.LINE_AA)
                        time.sleep(5)
                        sys.exit()
                    elif res is False:
                        print("User won!")
                        sys.exit()
                    user_move = ''
            cv2.imshow("Chopsticks game - AI", img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video.release()
        cv2.destroyAllWindows()
        return

    def validate(self, engineHand, humanHand):
        if engineHand.fingerCount + humanHand.fingerCount == 5:
            return True
        if (engineHand.fingerCount + humanHand.fingerCount) + engineHand.fingerCount == 5:
            return False
        if engineHand.name == "right":
            otherHand = self.engineLeftHand
        elif engineHand.name == "left":
            otherHand = self.engineRightHand

        if (engineHand.fingerCount + humanHand.fingerCount) + otherHand.fingerCount == 5:
            return False
        return "OK"

    def runOptimalMove(self, img, w, h):  # GREEDY!!
        fontScale = (w * h) / (1000 * 1000)
        fontScale = 0.3072

        def performMove(engineHand, humanHand):
            print("Engine attacked on : ", humanHand.name,
                  "with ", engineHand.name)
            cv2.putText(img, f"Engine attacked on {humanHand.name} with {engineHand.name}", (
                300, 250), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
            self.lastEngineMove = f"Engine attacked on {humanHand.name} with {engineHand.name}"
            time.sleep(2)
            humanHand.fingerCount = (
                humanHand.fingerCount + engineHand.fingerCount) % 5
            if humanHand.fingerCount == 5 or humanHand.fingerCount == 0:
                humanHand.in_play = False
                humanHand.fingerCount = 0
                print("human's", humanHand.name,
                      "hand is now out of play!")
                cv2.putText(img, f"Human's {humanHand.name} hand is now out of play", (
                    300, 250), cv2.FONT_HERSHEY_SIMPLEX, fontScale,  (255, 0, 0), 1, lineType=cv2.LINE_AA)
                otherHand = self.humanRightHand if humanHand.name == "left" else self.humanLeftHand
                if not otherHand.in_play:
                    self.display_stats()
                    return True
                return
        optimals = []
        for combination in self.combinations:
            engineHand, humanHand = combination.hand1, combination.hand2
            if not humanHand.in_play or not engineHand.in_play:
                continue
            optimal = self.validate(engineHand, humanHand)
            if optimal == "OK":  # One possible solution found
                optimals.append((engineHand, humanHand))
                continue
            if optimal is True:  # Most optimal found!
                if performMove(engineHand, humanHand):
                    return True
                return
        if not optimals:  # No optimal solutions found!
            return False

        engineHand, humanHand = random.choice(optimals)
        # Well, computer decides to make a random move, might get lucky if user does not make the right move!
        if performMove(engineHand, humanHand):
            return True


game_engine = Engine()
game_engine.start_game()
