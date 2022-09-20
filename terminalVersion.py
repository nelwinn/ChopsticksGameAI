import random


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

        self.combinations = [Combination(self.engineRightHand, self.humanRightHand),
                             Combination(self.engineLeftHand,
                                         self.humanLeftHand),
                             Combination(self.engineRightHand,
                                         self.humanLeftHand),
                             Combination(self.engineLeftHand, self.humanRightHand)]

    def display_stats(self):
        print("EngineLeftHand: ", self.engineLeftHand.fingerCount,
              "\tEngineRightHand: ", self.engineRightHand.fingerCount)

        print("HumanLeftHand: ", self.humanLeftHand.fingerCount,
              "\thumanRightHand: ", self.humanRightHand.fingerCount)
        print()

    def start_game(self):
        while True:
            self.display_stats()
            print("AL-L means attack computer's left hand with your Left hand")
            print("S-LR means shift your left hand scores to Right hand")
            print()
            user_move = input(
                "Make the move (AL-L, AL-R, AR-L, AR-R, S-LR, S-RL): ")
            if user_move.startswith("S"):
                hands = user_move.split("-")[1]
                userhand1, userhand2 = hands[0], hands[1]

                userhand1 = self.humanLeftHand if userhand1 == "L" else self.humanRightHand
                userhand2 = self.humanRightHand if userhand2 == "R" else self.humanLeftHand
                print(userhand1, userhand2)

                if userhand1.in_play is False:
                    print(
                        f"Invalid shift move, Your {userhand1.name} hand is out of play!")
                    continue
                scoresToTransfer = int(input("Enter the score to transfer: "))

                if userhand1.fingerCount < scoresToTransfer:
                    print(userhand1.fingerCount, userhand1.name)
                    print("Invalid move: not enough scores to transfer")
                    continue
                userhand1.fingerCount = userhand1.fingerCount - scoresToTransfer
                if userhand1.fingerCount == 0:
                    userhand1.in_play = False  # Oops, why did user transfer the entire scores?

                userhand2.fingerCount = (
                    userhand2.fingerCount + scoresToTransfer) % 5
                userhand2.im_play = True
                print(
                    f"User Transferred {scoresToTransfer} scores from {userhand1.name} to {userhand2.name}")
                continue
            enginehand, userhand = user_move.split('-')
            engineHand = self.engineLeftHand if enginehand == "AL" else self.engineRightHand
            userHand = self.humanLeftHand if userhand == "L" else self.humanRightHand
            if user_move.startswith("AL"):
                if not self.engineLeftHand.in_play:
                    print("EngineLeftHand is not in play!")
                    continue
                elif not userHand.in_play:
                    print("You are not allowed to use that hand!")
                    continue
                self.engineLeftHand.fingerCount = (
                    self.engineLeftHand.fingerCount + userHand.fingerCount) % 5
                if self.engineLeftHand.fingerCount == 5:
                    self.engineLeftHand.in_play = False
                    self.engineLeftHand.fingerCount = 0
                    print("Engine's left hand is now out of play!")
                    if self.engineRightHand.in_play is False:
                        print("User won!")
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
                        return False
            res = self.runOptimalMove()
            if res:
                print("Computer won!")
            elif res is False:
                print("User won!")

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

    def runOptimalMove(self):
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


game_engine = Engine()
game_engine.start_game()
