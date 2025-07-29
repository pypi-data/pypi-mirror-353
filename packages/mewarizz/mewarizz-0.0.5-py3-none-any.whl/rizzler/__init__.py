import random
import time

class gyattRizzler:
    @classmethod
    def plines(self):
        pickup_lines = ["Ow! I hurt my leg! Falling for you.", "Are you the Eiffel Tower? Because I fell for you.", "Hey, there\'s a fire truck over there for you, because you\'re hot."]
        print(random.choice(pickup_lines))

    @classmethod
    def pmoves(self):
        print("Use the pickup lines, and if you get the hurt leg rizz line, then pretend you hurt your leg.")
class mewRizzler:
    @classmethod
    def teachMew(self):
        print("1. Raise an eyebrow.")
        time.sleep(2)
        print("2. Do a duck face.")
        time.sleep(2)
        print("3. Tilt your head.")
        time.sleep(2)
        print("4. On the upper side, use your finger and slide it through your lower jaw.")
        time.sleep(2)
        print("5. Repeat on the other side.")

class ultimateRizzler:
    @classmethod
    def ultimateRizzAdvice(self,yeno):
        if yeno == "yes":
            print("Just be sweet, be friends, and develop friendship over time.")
            print("Else, if you want manual rizz, switch your class to gyattRizzler.")
        elif yeno == "no":
            print("All right, no rizz advice for you.")
        elif yeno == "maybe":
            print("Come back when you\'ve made your decision. Then we\'ll talk rizz.")
        else:
            print("No understandable input, no advice.")

class roast:
    @staticmethod
    def beTheAlpha():
        user_input = input("ONLY use this in case you have to roast an opponent in a rizz battle. Are you sure you\'d like to proceed? ").lower()
        if "yes" in user_input or "of course" in user_input or "sure" in user_input or "yeah" in user_input or "absolutely" in user_input:
            print("You\'re so fat, the weight scale said \"To be continued...\"")
            time.sleep(2)
            print("You\'re so ugly, if ugliness was a brick, you\'d be the great wall of China.")
            time.sleep(2)
            print("You\'re so dumb, you put sugar under your bed just so you could have sweet dreams.")
            time.sleep(2)
            print("You\'re so dumb, you used a ruler to see how long you slept.")
            time.sleep(2)
            print("You\'re so fat, your belt size is equator.")
            time.sleep(2)
            print("You\'re so fat, when you sat on an iPhone, it turned into an iPad.")
        elif "no" in user_input or "not" in user_input or "nah" in user_input:
            print("Ok. No roasts to be the Alpha.")
        else:
            print("Please put a valid input.")
