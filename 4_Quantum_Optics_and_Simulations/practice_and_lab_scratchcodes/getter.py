#Header Files

import sys
import math
import random
import threading
import time
from functools import reduce


#Global Variables

#Functions

#main()

class rect:
    def __init__(self, h = "0", w = "0"):
        self.w = w
        self.h = h
    @property
    def h(self):
        print("Retriving Height")
        return self.__h

    @h.setter
    def h(self, value):
        if value.isdigit():
            self._h = value
        else:
            print("NUMBERS ONLY")
    @property
    def w(self):
        print("Retriving Width")
        return self.__w

    @w.setter
    def w(self, value):
        if value.isdigit():
            self._w = value
        else:
            print("NUMBERS ONLY")

    def area(self):
        return int(self.__w) * int(self.__h)

sq = rect()
sq.h="10"
sq.w="5"
print("AREA", sq.area())

